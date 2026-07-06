const STORAGE_KEY = "mova-sports-v1";
const SESSION_KEY = "mova-sports-session";
const OLD_KEYS = ["loja-nova-base-v1", "fashion-store-management-v2", "clothing-products-v1"];

OLD_KEYS.forEach((key) => localStorage.removeItem(key));

const todayIso = toDateInput(new Date());
const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const paymentLabels = { cash: "Dinheiro", pix: "PIX", debit: "Débito", credit: "Crédito", storeCredit: "Crediário" };
const BACKEND_ENABLED = location.protocol !== "file:";
const STATE_API_URL = "/api/state";
const MODULE_API_ENDPOINTS = {
  products: "/api/products",
  customers: "/api/customers",
  suppliers: "/api/suppliers",
  brands: "/api/brands",
  categories: "/api/categories",
  users: "/api/users",
  sales: "/api/sales",
  receivables: "/api/receivables",
  payables: "/api/payables",
  cash: "/api/cash-movements",
  cashClosings: "/api/cash-closings",
  returns: "/api/returns",
};

let db = loadDb();
let session = loadSession();
let cart = [];
let productPhotoData = "";
let productPhotoFile = null;
let catalogViewMode = "grid";
let serverSaveTimer = null;
let serverStateLoaded = !BACKEND_ENABLED;
let hasLocalChanges = false;
let localChangeVersion = 0;
let dashboardApiCache = null;
let dashboardApiKey = "";
let dashboardApiLoading = false;
let reportsApiCache = null;
let reportsApiKey = "";
let reportsApiLoading = false;
let backups = [];
let backupsLoaded = false;
let backupsLoading = false;
let databaseStatus = null;
let databaseStatusLoaded = false;
let databaseStatusLoading = false;
let auditLogs = [];
let auditLogsLoaded = false;
let auditLogsLoading = false;
let selectedSaleHistoryKey = "";

const els = {};
document.querySelectorAll("[id]").forEach((element) => {
  els[element.id] = element;
});
let chartTooltip = null;

bindEvents();
applySession();
renderAll();
syncSessionFromServer();

function bindEvents() {
  document.querySelectorAll(".tab-button").forEach((button) => button.addEventListener("click", () => activateTab(button.dataset.tab)));
  document.querySelectorAll(".subtab").forEach((button) => button.addEventListener("click", () => activateSubtab(button.dataset.subtab)));
  document.querySelectorAll(".cadastro-card").forEach((button) => button.addEventListener("click", () => activateSubtab(button.dataset.subtab)));
  ["cashStart", "cashEnd", "reportStart", "reportEnd", "manualReceiptDate", "cancelSaleDate", "cancelSaleEndDate", "creditReceiveDate", "payableStart", "payableEnd", "bankAccountDate", "cashClosingDate"].forEach((id) => els[id].value = todayIso);

  els.loginForm.addEventListener("submit", login);
  els.logoutButton.addEventListener("click", logout);
  els.productForm.addEventListener("submit", saveProduct);
  els.clearProductButton.addEventListener("click", resetProductForm);
  els.backCadastroButton.addEventListener("click", showCadastroHome);
  els.exportProductsButton.addEventListener("click", exportProducts);
  els.exportCustomersButton.addEventListener("click", exportCustomers);
  els.productTableSearch.addEventListener("input", renderProducts);
  els.productTableFilter.addEventListener("input", renderProducts);
  els.productPhoto.addEventListener("change", readProductPhoto);
  els.customerForm.addEventListener("submit", saveCustomer);
  els.clearCustomerButton.addEventListener("click", resetCustomerForm);
  els.supplierForm.addEventListener("submit", saveSupplier);
  els.brandForm.addEventListener("submit", (event) => saveSimpleName(event, "brands", els.brandName));
  els.categoryForm.addEventListener("submit", (event) => saveSimpleName(event, "categories", els.categoryName));
  els.userForm.addEventListener("submit", saveUser);

  ["customerListSearch", "supplierListSearch", "brandListSearch", "categoryListSearch", "userListSearch", "catalogSearch", "catalogCategoryFilter", "catalogBrandFilter", "stockSearch", "stockCategoryFilter", "stockBrandFilter", "stockStatusFilter", "saleProductSearch", "saleCustomerSearch", "saleDiscount", "saleHistorySearch", "cancelSaleSearch", "cancelSaleDate", "cancelSaleEndDate", "creditCustomerSearch", "payableSearch", "payableCategoryFilter", "payableFilter", "payableStart", "payableEnd", "cashStart", "cashEnd", "cashMethodFilter", "cashTypeFilter", "reportStart", "reportEnd", "dashSalesRange"].forEach((id) => {
    els[id].addEventListener("input", renderAll);
  });

  els.catalogPdfButton.addEventListener("click", exportCatalogPdf);
  els.catalogClearFiltersButton.addEventListener("click", clearCatalogFilters);
  els.catalogGridViewButton.addEventListener("click", () => setCatalogView("grid"));
  els.catalogListViewButton.addEventListener("click", () => setCatalogView("list"));
  els.creditReceiveForm.addEventListener("submit", saveCreditReceipt);
  els.creditReceiveList.addEventListener("input", renderCreditReceiveTotal);
  els.creditReceiveCloseButton.addEventListener("click", closeCreditReceiveModal);
  els.creditReceiveCancelButton.addEventListener("click", closeCreditReceiveModal);
  els.creditNewCustomerButton.addEventListener("click", () => {
    resetCustomerForm();
    activateTab("cadastros");
    activateSubtab("cad-cliente");
  });
  els.stockExportButton.addEventListener("click", exportProducts);
  els.stockNewProductButton.addEventListener("click", () => {
    resetProductForm();
    activateTab("cadastros");
    activateSubtab("cad-produto");
  });
  els.clearSaleButton.addEventListener("click", clearSale);
  els.addPaymentButton.addEventListener("click", () => addPaymentRow("cash"));
  els.finishSaleButton.addEventListener("click", finishSale);
  els.returnForm.addEventListener("submit", registerReturn);
  els.returnProductSearch.addEventListener("input", renderReturnSaleItems);
  els.manualReceiptForm.addEventListener("submit", saveManualReceipt);
  els.manualReceiptForm.addEventListener("input", renderManualReceiptSummary);
  els.payableForm.addEventListener("submit", savePayable);
  els.payableNewButton.addEventListener("click", () => els.payableFormPanel.hidden = !els.payableFormPanel.hidden);
  els.cashClosingButton.addEventListener("click", () => els.cashClosingPanel.hidden = !els.cashClosingPanel.hidden);
  els.cashClosingForm.addEventListener("submit", saveCashClosing);
  els.cashClosingForm.addEventListener("input", renderCashClosingSummary);
  els.bankAccountButton.addEventListener("click", () => els.bankAccountPanel.hidden = !els.bankAccountPanel.hidden);
  els.bankAccountForm.addEventListener("submit", saveBankAccountEntry);
  els.cashMovementButton.addEventListener("click", () => els.cashMovementPanel.hidden = !els.cashMovementPanel.hidden);
  els.cashMovementForm.addEventListener("submit", saveCashMovement);
  els.cardReceiptForm.addEventListener("submit", receiveCards);
  els.refreshDatabaseButton.addEventListener("click", () => loadDatabaseStatus(true));
  els.refreshBackupsButton.addEventListener("click", () => loadBackups(true));
  els.createBackupButton.addEventListener("click", createBackup);
  els.exportDataButton.addEventListener("click", exportSystemData);
  els.refreshAuditButton.addEventListener("click", () => loadAuditLogs(true));
  ["auditSearch"].forEach((id) => els[id].addEventListener("input", renderAuditLogs));
  ["auditModuleFilter", "auditActionFilter", "auditLimit"].forEach((id) => els[id].addEventListener("input", () => loadAuditLogs(true)));
}

function defaultDb() {
  return {
    users: [{ id: "admin", name: "Administrador", login: "admin", password: "1234", role: "admin" }],
    products: [],
    customers: [],
    suppliers: [],
    brands: [],
    categories: [],
    sales: [],
    receivables: [],
    payables: [],
    cash: [],
    cashClosings: [],
    returns: [],
  };
}

function loadDb() {
  try {
    const loaded = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if (!loaded) return defaultDb();
    return mergeDb(loaded);
  } catch {
    return defaultDb();
  }
}

function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(db));
  invalidateDashboardCache();
  if (!BACKEND_ENABLED) {
    hasLocalChanges = true;
    localChangeVersion += 1;
  }
}

function persistLocalOnly() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(db));
  invalidateDashboardCache();
}

function invalidateDashboardCache() {
  dashboardApiCache = null;
  dashboardApiKey = "";
  reportsApiCache = null;
  reportsApiKey = "";
}

async function syncFromServer() {
  if (!BACKEND_ENABLED) return;
  try {
    const serverDb = await loadDbFromModuleApis();
    applyServerDb(serverDb);
    serverStateLoaded = true;
  } catch (error) {
    console.warn(error);
    await syncFromStateFallback();
  }
}

async function loadDbFromModuleApis() {
  const entries = await Promise.all(Object.entries(MODULE_API_ENDPOINTS).map(async ([key, url]) => {
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) throw new Error(`Falha ao carregar ${key}.`);
    const payload = await response.json();
    return [key, Array.isArray(payload.data) ? payload.data : []];
  }));
  const moduleDb = mergeDb(Object.fromEntries(entries));
  moduleDb.users = mergeServerUsers(moduleDb.users);
  return moduleDb;
}

function mergeServerUsers(users) {
  const localUsers = db.users || [];
  const baseUsers = defaultDb().users;
  return (users || []).map((user) => {
    const local = localUsers.find((item) => item.id === user.id || item.login === user.login);
    const base = baseUsers.find((item) => item.id === user.id || item.login === user.login);
    return { ...user, password: user.password || local?.password || base?.password || "" };
  });
}

function applyServerDb(serverDb) {
  db = serverDb;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(db));
  hasLocalChanges = false;
  invalidateDashboardCache();
  renderAll();
}

async function syncFromStateFallback() {
  try {
    const response = await fetch(STATE_API_URL, { cache: "no-store" });
    if (!response.ok) throw new Error("Falha ao carregar dados do servidor.");
    const payload = await response.json();
    if (payload?.data) applyServerDb(mergeDb(payload.data));
  } catch (fallbackError) {
    console.warn(fallbackError);
  } finally {
    serverStateLoaded = true;
  }
}

function mergeDb(loaded) {
  const base = defaultDb();
  const merged = { ...base, ...(loaded || {}) };
  Object.keys(base).forEach((key) => {
    if (!Array.isArray(merged[key])) merged[key] = base[key];
  });
  if (!merged.users.length) merged.users = base.users;
  return merged;
}

function hasBusinessData(data) {
  return ["products", "customers", "suppliers", "brands", "categories", "sales", "receivables", "payables", "cash", "returns"].some((key) => data?.[key]?.length);
}

function scheduleServerPersist() {
  return;
}

async function saveStateToServer(version = localChangeVersion) {
  void version;
  return false;
}

function loadSession() {
  try {
    return JSON.parse(sessionStorage.getItem(SESSION_KEY)) || null;
  } catch {
    return null;
  }
}

function saveSession() {
  if (session) sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
  else sessionStorage.removeItem(SESSION_KEY);
}

async function login(event) {
  event.preventDefault();
  els.loginMessage.hidden = true;
  if (BACKEND_ENABLED) {
    try {
      const response = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ login: els.loginUser.value.trim(), password: els.loginPassword.value }),
      });
      const payload = await response.json();
      if (response.ok && payload.user) {
        session = payload.user;
        saveSession();
        applySession();
        await syncFromServer();
        renderAll();
        return;
      }
      els.loginMessage.textContent = payload.error || "Usuário ou senha inválidos.";
      els.loginMessage.hidden = false;
      return;
    } catch (error) {
      console.warn(error);
    }
  }
  const user = db.users.find((item) => item.login === els.loginUser.value.trim() && item.password === els.loginPassword.value);
  if (!user) {
    els.loginMessage.textContent = "Usuário ou senha inválidos.";
    els.loginMessage.hidden = false;
    return;
  }
  session = { id: user.id, name: user.name, role: user.role };
  saveSession();
  applySession();
}

async function logout() {
  if (BACKEND_ENABLED) {
    try {
      await fetch("/api/logout", { method: "POST" });
    } catch (error) {
      console.warn(error);
    }
  }
  session = null;
  saveSession();
  applySession();
}

async function syncSessionFromServer() {
  if (!BACKEND_ENABLED) return;
  try {
    const response = await fetch("/api/session", { cache: "no-store" });
    if (!response.ok) return;
    const payload = await response.json();
    if (payload.user) {
      session = payload.user;
      saveSession();
      applySession();
      await syncFromServer();
      renderAll();
    } else {
      session = null;
      saveSession();
      applySession();
      renderAll();
    }
  } catch (error) {
    console.warn(error);
  }
}

function applySession() {
  const logged = Boolean(session);
  els.loginScreen.hidden = logged;
  els.currentUserLabel.textContent = logged ? session.name : "";
  els.currentUserRole.textContent = logged ? (session.role === "admin" ? "Administrador" : "Operador") : "";
  document.querySelectorAll(".admin-only").forEach((element) => element.hidden = session?.role !== "admin");
  document.querySelectorAll(".manager-only").forEach((element) => element.hidden = session?.role !== "admin");
}

function isAdmin() {
  return session?.role === "admin";
}

function activateTab(tabId) {
  document.querySelectorAll(".tab-button").forEach((button) => button.classList.toggle("active", button.dataset.tab === tabId));
  document.querySelectorAll(".tab-panel").forEach((panel) => panel.classList.toggle("active", panel.id === tabId));
  if (tabId === "cadastros") showCadastroHome();
  if (tabId === "configuracoes") {
    loadDatabaseStatus();
    loadBackups();
    loadAuditLogs(true);
  }
}

function activateSubtab(tabId) {
  const parent = document.getElementById(tabId).closest(".tab-panel");
  parent.querySelectorAll(".subtab").forEach((button) => button.classList.toggle("active", button.dataset.subtab === tabId));
  parent.querySelectorAll(".subtab-panel").forEach((panel) => panel.classList.toggle("active", panel.id === tabId));
  updateCadastroHeader(tabId);
}

function showCadastroHome() {
  activateSubtab("cad-home");
}

function updateCadastroHeader(tabId) {
  const labels = {
    "cad-home": ["Cadastros", "Escolha qual cadastro deseja abrir."],
    "cad-produto": ["Cadastro de Produtos", "Cadastre e gerencie os produtos da sua loja."],
    "cad-cliente": ["Cadastro de Clientes", "Cadastre clientes e acompanhe limite de crédito."],
    "cad-fornecedor": ["Cadastro de Fornecedores", "Gerencie fornecedores e dados fiscais."],
    "cad-marca": ["Cadastro de Marcas", "Organize as marcas dos produtos."],
    "cad-categoria": ["Cadastro de Categorias", "Organize linhas e grupos de produtos."],
    "cad-usuario": ["Cadastro de Usuários", "Gerencie acessos e permissões do sistema."],
  };
  const [title, subtitle] = labels[tabId] || labels["cad-home"];
  els.cadastroTitle.textContent = title;
  els.cadastroSubtitle.textContent = subtitle;
  els.cadastroPageActions.hidden = tabId === "cad-home";
  document.querySelectorAll(".product-only-action").forEach((element) => element.hidden = tabId !== "cad-produto");
  document.querySelectorAll(".customer-only-action").forEach((element) => element.hidden = tabId !== "cad-cliente");
}

async function saveProduct(event) {
  event.preventDefault();
  const id = els.editingProductId.value || createId();
  const barcode = els.productBarcode.value.trim();
  const duplicate = db.products.some((product) => product.barcode === barcode && product.id !== id);
  if (duplicate) return alert("Código de barras já cadastrado.");
  const existing = db.products.find((product) => product.id === id);
  const photo = await resolveProductPhoto(existing?.photo || "");
  if (photo === null) return;
  const product = {
    id,
    barcode,
    name: els.productName.value.trim(),
    size: els.productSize.value.trim(),
    color: els.productColor.value.trim(),
    gender: els.productGender.value,
    category: els.productCategory.value.trim(),
    brand: els.productBrand.value.trim(),
    stock: Math.max(0, Math.floor(readNumber(els.productStock.value))),
    minStock: Math.max(0, Math.floor(readNumber(els.productMinStock.value))),
    description: els.productDescription.value.trim(),
    active: els.productActive.checked,
    cost: readNumber(els.productCost.value),
    price: readNumber(els.productPrice.value),
    photo,
    updatedAt: new Date().toISOString(),
  };
  if (BACKEND_ENABLED) {
    try {
      const response = await fetch(existing ? `/api/products/${encodeURIComponent(id)}` : "/api/products", {
        method: existing ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(product),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        alert(payload.error || "Não foi possível salvar o produto.");
        return;
      }
      applyProductLocally(payload.data || product);
      persistLocalOnly();
      resetProductForm();
      renderAll();
      return;
    } catch (error) {
      console.warn(error);
      alert("Não foi possível conectar ao servidor para salvar o produto.");
      return;
    }
  }

  applyProductLocally(product);
  persist();
  resetProductForm();
  renderAll();
}

function applyProductLocally(product) {
  if (!db.brands.includes(product.brand) && product.brand) db.brands.push(product.brand);
  if (!db.categories.includes(product.category) && product.category) db.categories.push(product.category);
  db.products = db.products.some((item) => item.id === product.id)
    ? db.products.map((item) => item.id === product.id ? product : item)
    : [product, ...db.products];
}

function resetProductForm() {
  els.productForm.reset();
  els.editingProductId.value = "";
  els.productStock.value = "0";
  els.productMinStock.value = "0";
  els.productActive.checked = true;
  els.productCost.value = "0";
  els.productPrice.value = "0";
  productPhotoData = "";
  productPhotoFile = null;
}

function editProduct(id) {
  const product = db.products.find((item) => item.id === id);
  if (!product) return;
  els.editingProductId.value = product.id;
  els.productBarcode.value = product.barcode;
  els.productName.value = product.name;
  els.productSize.value = product.size;
  els.productColor.value = product.color;
  els.productGender.value = product.gender;
  els.productCategory.value = product.category;
  els.productBrand.value = product.brand;
  els.productStock.value = product.stock;
  els.productMinStock.value = product.minStock || 0;
  els.productDescription.value = product.description || "";
  els.productActive.checked = product.active !== false;
  els.productCost.value = fixed(product.cost);
  els.productPrice.value = fixed(product.price);
  productPhotoData = product.photo || "";
  productPhotoFile = null;
  activateTab("cadastros");
  activateSubtab("cad-produto");
}

function readProductPhoto() {
  const file = els.productPhoto.files?.[0];
  if (!file) return;
  productPhotoFile = file;
  if (BACKEND_ENABLED) {
    productPhotoData = "";
    return;
  }
  const reader = new FileReader();
  reader.addEventListener("load", () => productPhotoData = String(reader.result || ""));
  reader.readAsDataURL(file);
}

async function resolveProductPhoto(fallback = "") {
  if (!BACKEND_ENABLED) return productPhotoData || fallback;
  if (!productPhotoFile) return productPhotoData || fallback;
  const formData = new FormData();
  formData.append("photo", productPhotoFile);
  try {
    const response = await fetch("/api/uploads/product-photo", { method: "POST", body: formData });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      alert(payload.error || "Não foi possível enviar a foto do produto.");
      return null;
    }
    productPhotoFile = null;
    productPhotoData = payload.data?.url || "";
    return productPhotoData || fallback;
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para enviar a foto.");
    return null;
  }
}

async function saveCustomer(event) {
  event.preventDefault();
  const id = els.editingCustomerId.value || createId();
  const existing = db.customers.find((customer) => customer.id === id);
  const customer = {
    id,
    code: existing?.code || nextCustomerCode(),
    name: els.customerName.value.trim(),
    cpf: els.customerCpf.value.trim(),
    rg: els.customerRg.value.trim(),
    birth: els.customerBirth.value,
    whatsapp: els.customerWhatsapp.value.trim(),
    email: els.customerEmail.value.trim(),
    address: els.customerAddress.value.trim(),
    city: els.customerCity.value.trim(),
    district: els.customerDistrict.value.trim(),
    zip: els.customerZip.value.trim(),
    limit: readNumber(els.customerLimit.value),
    status: existing?.status || "active",
  };

  if (BACKEND_ENABLED) {
    try {
      const response = await fetch(existing ? `/api/customers/${encodeURIComponent(id)}` : "/api/customers", {
        method: existing ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(customer),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        alert(payload.error || "Não foi possível salvar o cliente.");
        return;
      }
      applyCustomerLocally(payload.data || customer);
      persistLocalOnly();
      resetCustomerForm();
      renderAll();
      return;
    } catch (error) {
      console.warn(error);
      alert("Não foi possível conectar ao servidor para salvar o cliente.");
      return;
    }
  }

  applyCustomerLocally(customer);
  persist();
  resetCustomerForm();
  renderAll();
}

function applyCustomerLocally(customer) {
  db.customers = db.customers.some((item) => item.id === customer.id)
    ? db.customers.map((item) => item.id === customer.id ? customer : item)
    : [customer, ...db.customers];
}

function resetCustomerForm() {
  els.customerForm.reset();
  els.editingCustomerId.value = "";
  els.customerCode.value = nextCustomerCode();
  els.customerLimit.value = "0";
}

function editCustomer(id) {
  const customer = db.customers.find((item) => item.id === id);
  if (!customer) return;
  els.editingCustomerId.value = customer.id;
  els.customerCode.value = customer.code;
  els.customerName.value = customer.name;
  els.customerCpf.value = customer.cpf;
  els.customerRg.value = customer.rg;
  els.customerBirth.value = customer.birth;
  els.customerWhatsapp.value = customer.whatsapp;
  els.customerEmail.value = customer.email;
  els.customerAddress.value = customer.address;
  els.customerCity.value = customer.city;
  els.customerDistrict.value = customer.district;
  els.customerZip.value = customer.zip;
  els.customerLimit.value = fixed(customer.limit);
  activateSubtab("cad-cliente");
}

async function saveSupplier(event) {
  event.preventDefault();
  if (!validCnpj(els.supplierCnpj.value)) return alert("CNPJ invalido.");
  const id = els.editingSupplierId.value || createId();
  const existing = db.suppliers.find((supplier) => supplier.id === id);
  const supplier = {
    id,
    name: els.supplierName.value.trim(),
    cnpj: els.supplierCnpj.value.trim(),
    phone: els.supplierPhone.value.trim(),
    email: els.supplierEmail.value.trim(),
    address: els.supplierAddress.value.trim(),
  };
  if (BACKEND_ENABLED) {
    try {
      const response = await fetch(existing ? `/api/suppliers/${encodeURIComponent(id)}` : "/api/suppliers", {
        method: existing ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(supplier),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        alert(payload.error || "Não foi possível salvar o fornecedor.");
        return;
      }
      applySupplierLocally(payload.data || supplier);
      persistLocalOnly();
      resetSupplierForm();
      renderAll();
      return;
    } catch (error) {
      console.warn(error);
      alert("Não foi possível conectar ao servidor para salvar o fornecedor.");
      return;
    }
  }

  applySupplierLocally(supplier);
  persist();
  resetSupplierForm();
  renderAll();
}

function applySupplierLocally(supplier) {
  db.suppliers = db.suppliers.some((item) => item.id === supplier.id)
    ? db.suppliers.map((item) => item.id === supplier.id ? supplier : item)
    : [supplier, ...db.suppliers];
}

async function saveSimpleName(event, collection, input) {
  event.preventDefault();
  const value = input.value.trim();
  const editingInput = collection === "brands" ? els.editingBrandName : els.editingCategoryName;
  const previous = editingInput.value;
  const duplicate = db[collection].some((item) => normalize(item) === normalize(value) && normalize(item) !== normalize(previous));
  if (!value) return;
  if (duplicate) return alert("Nome já cadastrado.");
  if (BACKEND_ENABLED) {
    try {
      const endpoint = collection === "brands" ? "/api/brands" : "/api/categories";
      const response = await fetch(previous ? `${endpoint}/${encodeURIComponent(previous)}` : endpoint, {
        method: previous ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: value }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        alert(payload.error || "Não foi possível salvar o cadastro.");
        return;
      }
      applySimpleNameLocally(collection, payload.data || value, previous);
      input.value = "";
      editingInput.value = "";
      persistLocalOnly();
      renderAll();
      return;
    } catch (error) {
      console.warn(error);
      alert("Não foi possível conectar ao servidor para salvar o cadastro.");
      return;
    }
  }
  applySimpleNameLocally(collection, value, previous);
  input.value = "";
  editingInput.value = "";
  persist();
  renderAll();
}

function applySimpleNameLocally(collection, value, previous = "") {
  if (previous) {
    db[collection] = db[collection].map((item) => item === previous ? value : item);
    const field = collection === "brands" ? "brand" : "category";
    db.products = db.products.map((product) => product[field] === previous ? { ...product, [field]: value } : product);
  } else if (!db[collection].includes(value)) {
    db[collection].push(value);
  }
}

async function saveUser(event) {
  event.preventDefault();
  if (!isAdmin()) return alert("Apenas admin pode criar usuários.");
  const id = els.editingUserId.value || createId();
  const existing = db.users.find((user) => user.id === id);
  const duplicate = db.users.some((user) => user.login === els.userLogin.value.trim() && user.id !== id);
  if (duplicate) return alert("Usuário já cadastrado.");
  const user = {
    id,
    name: els.userName.value.trim(),
    login: els.userLogin.value.trim(),
    password: els.userPassword.value,
    role: els.userRole.value,
    active: existing?.active ?? true,
  };
  if (!existing && !user.password) return alert("Senha é obrigatória para novo usuário.");

  if (BACKEND_ENABLED) {
    try {
      const response = await fetch(existing ? `/api/users/${encodeURIComponent(id)}` : "/api/users", {
        method: existing ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(user),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        alert(payload.error || "Não foi possível salvar o usuário.");
        return;
      }
      applyUserLocally({ ...(payload.data || user), password: user.password || existing?.password || "" });
      persistLocalOnly();
      resetUserForm();
      renderAll();
      return;
    } catch (error) {
      console.warn(error);
      alert("Não foi possível conectar ao servidor para salvar o usuário.");
      return;
    }
  }

  applyUserLocally(user);
  persist();
  resetUserForm();
  renderAll();
}

function applyUserLocally(user) {
  db.users = db.users.some((item) => item.id === user.id)
    ? db.users.map((item) => item.id === user.id ? user : item)
    : [...db.users, user];
}

function resetSupplierForm() {
  els.supplierForm.reset();
  els.editingSupplierId.value = "";
}

function editSupplier(id) {
  const supplier = db.suppliers.find((item) => item.id === id);
  if (!supplier) return;
  els.editingSupplierId.value = supplier.id;
  els.supplierName.value = supplier.name;
  els.supplierCnpj.value = supplier.cnpj;
  els.supplierPhone.value = supplier.phone || "";
  els.supplierEmail.value = supplier.email || "";
  els.supplierAddress.value = supplier.address || "";
  activateSubtab("cad-fornecedor");
}

function editSimpleName(collection, value) {
  if (collection === "brands") {
    els.editingBrandName.value = value;
    els.brandName.value = value;
    activateSubtab("cad-marca");
    els.brandName.focus();
    return;
  }
  els.editingCategoryName.value = value;
  els.categoryName.value = value;
  activateSubtab("cad-categoria");
  els.categoryName.focus();
}

function resetUserForm() {
  els.userForm.reset();
  els.editingUserId.value = "";
  els.userPassword.required = true;
  els.userPassword.placeholder = "";
}

function editUser(id) {
  const user = db.users.find((item) => item.id === id);
  if (!user) return;
  els.editingUserId.value = user.id;
  els.userName.value = user.name;
  els.userLogin.value = user.login;
  els.userPassword.value = "";
  els.userPassword.required = false;
  els.userPassword.placeholder = "Deixe em branco para manter a senha atual";
  els.userRole.value = user.role;
  activateSubtab("cad-usuario");
}

function renderAll() {
  [
    applySession,
    renderOptions,
    renderCadastroCards,
    renderProducts,
    renderCustomers,
    renderSuppliers,
    renderSimpleLists,
    renderUsers,
    renderDashboard,
    renderCatalog,
    renderStock,
    renderSaleProducts,
    renderCart,
    renderSaleHistory,
    renderManualReceiptSummary,
    renderReturnSaleItems,
    renderCancelSales,
    renderCreditCustomers,
    renderPayables,
    renderCash,
    renderCards,
    renderReports,
  ].forEach((render) => safeRender(render));
}

function safeRender(render) {
  try {
    render();
  } catch (error) {
    console.error(`Erro ao renderizar ${render.name}.`, error);
  }
}

function renderCadastroCards() {
  els.productCardCount.textContent = `${db.products.length} produto${db.products.length === 1 ? "" : "s"} cadastrado${db.products.length === 1 ? "" : "s"}`;
  els.customerCardCount.textContent = `${db.customers.length} cliente${db.customers.length === 1 ? "" : "s"} cadastrado${db.customers.length === 1 ? "" : "s"}`;
  els.supplierCardCount.textContent = `${db.suppliers.length} fornecedor${db.suppliers.length === 1 ? "" : "es"}`;
  els.brandCardCount.textContent = `${db.brands.length} marca${db.brands.length === 1 ? "" : "s"} cadastrada${db.brands.length === 1 ? "" : "s"}`;
  els.categoryCardCount.textContent = `${db.categories.length} categoria${db.categories.length === 1 ? "" : "s"} cadastrada${db.categories.length === 1 ? "" : "s"}`;
  els.userCardCount.textContent = `${db.users.length} usuário${db.users.length === 1 ? "" : "s"} cadastrado${db.users.length === 1 ? "" : "s"}`;
}

function renderOptions() {
  fillDatalist(els.brandOptions, db.brands);
  fillDatalist(els.categoryOptions, db.categories);
  fillDatalist(els.customerOptions, db.customers.map((customer) => customer.name));
  fillDatalist(els.productOptions, db.products.map((product) => `${product.barcode} - ${product.name}`));
  fillDatalist(els.saleOptions, db.sales.map((sale) => sale.id));
  fillDatalist(els.supplierOptions, db.suppliers.map((supplier) => supplier.name));
  fillSelect(els.catalogCategoryFilter, db.categories, "Todas");
  fillSelect(els.catalogBrandFilter, db.brands, "Todas");
  fillSelect(els.stockCategoryFilter, db.categories, "Todas");
  fillSelect(els.stockBrandFilter, db.brands, "Todas");
  fillSelect(els.payableCategoryFilter, db.payables.map((item) => item.category), "Todas");
}

function fillDatalist(element, items) {
  element.innerHTML = "";
  items.filter(Boolean).sort((a, b) => a.localeCompare(b, "pt-BR")).forEach((item) => element.append(new Option(item, item)));
}

function fillSelect(element, items, allLabel) {
  const current = element.value || "all";
  element.innerHTML = "";
  element.append(new Option(allLabel, "all"));
  [...new Set(items.filter(Boolean))].sort((a, b) => a.localeCompare(b, "pt-BR")).forEach((item) => element.append(new Option(item, item)));
  element.value = [...element.options].some((option) => option.value === current) ? current : "all";
}

function renderProducts() {
  const query = normalize(els.productTableSearch.value);
  const filter = els.productTableFilter.value;
  const products = db.products.filter((product) => {
    const matchesQuery = !query || normalize(product.name).includes(query) || normalize(product.barcode).includes(query) || normalize(product.brand).includes(query);
    const matchesFilter = filter === "all" || (filter === "active" && product.active !== false) || (filter === "low" && product.stock <= (product.minStock || 0));
    return matchesQuery && matchesFilter;
  });
  renderProductTable(products);
}

function renderProductTable(products) {
  els.productList.innerHTML = "";
  if (!products.length) {
    els.productList.innerHTML = `<tr><td colspan="6" class="empty-cell">Nenhum produto encontrado.</td></tr>`;
    return;
  }
  products.forEach((product) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>
        <div class="product-cell">
          ${product.photo ? `<img src="${product.photo}" alt="">` : `<div class="product-mini-photo"></div>`}
          <div><strong>${escapeHtml(product.name)}</strong><small>${escapeHtml(product.barcode)}</small></div>
        </div>
      </td>
      <td>${escapeHtml(product.category || "-")}</td>
      <td>${money.format(product.price)}</td>
      <td class="${product.stock <= (product.minStock || 0) ? "danger-text" : ""}">${product.stock}</td>
      <td><span class="status-pill ${product.active === false ? "off" : ""}">${product.active === false ? "Inativo" : "Ativo"}</span></td>
      <td><div class="table-actions"></div></td>
    `;
    const actions = row.querySelector(".table-actions");
    actions.append(button("Editar", "icon-button", () => editProduct(product.id)));
    actions.append(button("Excluir", "icon-button danger-icon", () => deleteProduct(product.id)));
    els.productList.append(row);
  });
}

async function deleteProduct(id) {
  const product = db.products.find((item) => item.id === id);
  if (!product || !confirm(`Excluir ${product.name}?`)) return;
  if (BACKEND_ENABLED) {
    try {
      const response = await fetch(`/api/products/${encodeURIComponent(id)}`, { method: "DELETE" });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        alert(payload.error || "Não foi possível excluir o produto.");
        return;
      }
      db.products = db.products.filter((item) => item.id !== id);
      persistLocalOnly();
      renderAll();
      return;
    } catch (error) {
      console.warn(error);
      alert("Não foi possível conectar ao servidor para excluir o produto.");
      return;
    }
  }
  db.products = db.products.filter((item) => item.id !== id);
  persist();
  renderAll();
}

function exportProducts() {
  const rows = db.products.map((product) => ({
    codigo: product.barcode,
    nome: product.name,
    categoria: product.category,
    marca: product.brand,
    tamanho: product.size,
    cor: product.color,
    preco: fixed(product.price),
    estoque: product.stock,
  }));
  const csv = toCsv(rows);
  const blob = new Blob([`\uFEFF${csv}`], { type: "text/csv;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `produtos-${todayIso}.csv`;
  link.click();
  URL.revokeObjectURL(link.href);
}

function exportCustomers() {
  const rows = db.customers.map((customer) => {
    const stats = customerDebt(customer.id);
    return {
      codigo: customer.code,
      nome: customer.name,
      cpf: customer.cpf,
      rg: customer.rg,
      nascimento: customer.birth,
      whatsapp: customer.whatsapp,
      email: customer.email,
      endereco: customer.address,
      cidade: customer.city,
      bairro: customer.district,
      cep: customer.zip,
      limite_credito: fixed(customer.limit),
      saldo_aberto: fixed(stats.open),
    };
  });
  const csv = toCsv(rows);
  const blob = new Blob([`\uFEFF${csv}`], { type: "text/csv;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `clientes-${todayIso}.csv`;
  link.click();
  URL.revokeObjectURL(link.href);
}

function renderProductRows(container, products, editable) {
  container.innerHTML = "";
  container.classList.toggle("empty", products.length === 0);
  if (!products.length) {
    container.textContent = "Nenhum produto encontrado.";
    return;
  }
  products.forEach((product) => {
    const row = tableRow(
      product.name,
      `${product.barcode} | ${product.size || "-"} | ${product.color || "-"} | ${product.brand || "-"} | Estoque ${product.stock}`,
      money.format(product.price)
    );
    const actions = document.createElement("div");
    actions.className = "row-actions";
    if (editable) actions.append(button("Editar", "ghost", () => editProduct(product.id)));
    row.append(actions);
    container.append(row);
  });
}

function renderCustomers() {
  const query = normalize(els.customerListSearch.value);
  const customers = db.customers.filter((customer) => !query || normalize(customer.name).startsWith(query));
  els.customerList.innerHTML = "";
  if (!customers.length) {
    els.customerList.innerHTML = `<tr><td colspan="5" class="empty-cell">Nenhum cliente cadastrado.</td></tr>`;
    return;
  }
  customers.forEach((customer) => {
    const stats = customerDebt(customer.id);
    const row = document.createElement("tr");
    row.innerHTML = `
      <td><div class="customer-cell"><strong>${escapeHtml(customer.name)}</strong><small>${escapeHtml(customer.code || "-")}</small></div></td>
      <td><div class="customer-cell"><strong>${escapeHtml(customer.whatsapp || "-")}</strong><small>${escapeHtml(customer.email || "-")}</small></div></td>
      <td>${money.format(customer.limit || 0)}</td>
      <td class="${stats.open > 0 ? "danger-text" : ""}">${money.format(stats.open)}</td>
      <td><div class="table-actions"></div></td>
    `;
    const actions = row.querySelector(".table-actions");
    actions.append(button("Editar", "icon-button", () => editCustomer(customer.id)));
    els.customerList.append(row);
  });
}

function renderSuppliers() {
  els.supplierList.innerHTML = "";
  const term = normalize(els.supplierListSearch.value);
  const suppliers = db.suppliers.filter((supplier) => !term
    || normalize(supplier.name).includes(term)
    || normalize(supplier.cnpj).includes(term)
    || normalize(supplier.phone).includes(term)
    || normalize(supplier.email).includes(term));
  if (!db.suppliers.length) {
    els.supplierList.innerHTML = `<tr><td colspan="4" class="empty-cell">Nenhum fornecedor cadastrado.</td></tr>`;
    return;
  }
  if (!suppliers.length) {
    els.supplierList.innerHTML = `<tr><td colspan="4" class="empty-cell">Nenhum fornecedor encontrado.</td></tr>`;
    return;
  }
  suppliers.forEach((supplier) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td><strong>${escapeHtml(supplier.name)}</strong><small>${escapeHtml(supplier.address || "-")}</small></td>
      <td>${escapeHtml(supplier.cnpj)}</td>
      <td><strong>${escapeHtml(supplier.phone || "-")}</strong><small>${escapeHtml(supplier.email || "-")}</small></td>
      <td><div class="table-actions"></div></td>
    `;
    row.querySelector(".table-actions").append(button("Editar", "icon-button", () => editSupplier(supplier.id)));
    els.supplierList.append(row);
  });
}

function renderSimpleLists() {
  const brandTerm = normalize(els.brandListSearch.value);
  const categoryTerm = normalize(els.categoryListSearch.value);
  const brands = db.brands.filter((item) => !brandTerm || normalize(item).includes(brandTerm));
  const categories = db.categories.filter((item) => !categoryTerm || normalize(item).includes(categoryTerm));
  els.brandList.innerHTML = db.brands.length
    ? brands.map((item) => `<tr><td><strong>${escapeHtml(item)}</strong></td><td><div class="table-actions"><button class="icon-button" type="button" data-edit-brand="${escapeHtml(item)}">Editar</button></div></td></tr>`).join("") || `<tr><td colspan="2" class="empty-cell">Nenhuma marca encontrada.</td></tr>`
    : `<tr><td colspan="2" class="empty-cell">Nenhuma marca cadastrada.</td></tr>`;
  els.categoryList.innerHTML = db.categories.length
    ? categories.map((item) => `<tr><td><strong>${escapeHtml(item)}</strong></td><td><div class="table-actions"><button class="icon-button" type="button" data-edit-category="${escapeHtml(item)}">Editar</button></div></td></tr>`).join("") || `<tr><td colspan="2" class="empty-cell">Nenhuma categoria encontrada.</td></tr>`
    : `<tr><td colspan="2" class="empty-cell">Nenhuma categoria cadastrada.</td></tr>`;
  els.brandList.querySelectorAll("[data-edit-brand]").forEach((button) => button.addEventListener("click", () => editSimpleName("brands", button.dataset.editBrand)));
  els.categoryList.querySelectorAll("[data-edit-category]").forEach((button) => button.addEventListener("click", () => editSimpleName("categories", button.dataset.editCategory)));
}

function renderUsers() {
  els.userList.innerHTML = "";
  const term = normalize(els.userListSearch.value);
  const users = db.users.filter((user) => !term
    || normalize(user.name).includes(term)
    || normalize(user.login).includes(term)
    || normalize(user.role === "admin" ? "Admin" : "Operador").includes(term));
  if (!db.users.length) {
    els.userList.innerHTML = `<tr><td colspan="4" class="empty-cell">Nenhum usuário cadastrado.</td></tr>`;
    return;
  }
  if (!users.length) {
    els.userList.innerHTML = `<tr><td colspan="4" class="empty-cell">Nenhum usuário encontrado.</td></tr>`;
    return;
  }
  users.forEach((user) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td><strong>${escapeHtml(user.name)}</strong></td>
      <td>${escapeHtml(user.login)}</td>
      <td><span class="status-pill">${user.role === "admin" ? "Admin" : "Operador"}</span></td>
      <td><div class="table-actions"></div></td>
    `;
    row.querySelector(".table-actions").append(button("Editar", "icon-button", () => editUser(user.id)));
    els.userList.append(row);
  });
}

function renderCatalog() {
  const products = catalogProducts();
  els.catalogList.innerHTML = "";
  els.catalogList.classList.toggle("catalog-list-view", catalogViewMode === "list");
  els.catalogList.classList.toggle("catalog-grid-view", catalogViewMode === "grid");
  els.catalogList.classList.toggle("empty", products.length === 0);
  els.catalogGridViewButton.classList.toggle("active", catalogViewMode === "grid");
  els.catalogListViewButton.classList.toggle("active", catalogViewMode === "list");
  els.catalogCount.textContent = `${products.length} produto${products.length === 1 ? "" : "s"} encontrado${products.length === 1 ? "" : "s"}`;
  if (!products.length) {
    els.catalogList.textContent = "Nenhum produto cadastrado.";
    return;
  }
  products.forEach((product) => {
    const card = document.createElement("article");
    card.className = "catalog-card";
    card.innerHTML = `
      ${product.photo ? `<img src="${product.photo}" alt="">` : `<div class="photo-placeholder">Sem foto</div>`}
      <h3>${escapeHtml(product.name)}</h3>
      <small>${escapeHtml(product.barcode || "-")}</small>
      <p>${escapeHtml(product.size || "-")} | ${escapeHtml(product.color || "-")} | ${escapeHtml(product.brand || "-")}</p>
      <strong>${money.format(product.price)}</strong>
      <span class="catalog-stock-tag"><svg viewBox="0 0 24 24"><path d="m12 3 8 4.5v9L12 21l-8-4.5v-9L12 3Z"></path><path d="M4 7.5 12 12l8-4.5"></path><path d="M12 12v9"></path></svg>Estoque ${product.stock}</span>
    `;
    els.catalogList.append(card);
  });
}

function setCatalogView(mode) {
  catalogViewMode = mode;
  renderCatalog();
}

function catalogProducts() {
  const query = normalize(els.catalogSearch.value);
  const category = els.catalogCategoryFilter.value;
  const brand = els.catalogBrandFilter.value;
  return db.products.filter((product) => {
    const matchesQuery = !query
      || normalize(product.name).includes(query)
      || normalize(product.barcode).includes(query)
      || normalize(product.category).includes(query);
    const matchesCategory = category === "all" || product.category === category;
    const matchesBrand = brand === "all" || product.brand === brand;
    return matchesQuery && matchesCategory && matchesBrand && product.active !== false;
  });
}

function clearCatalogFilters() {
  els.catalogSearch.value = "";
  els.catalogCategoryFilter.value = "all";
  els.catalogBrandFilter.value = "all";
  renderAll();
}

function exportCatalogPdf() {
  openCatalogPrint(catalogProducts());
}

function openCatalogPrint(products) {
  const printWindow = window.open("", "_blank");
  if (!printWindow) {
    alert("Permita pop-ups para gerar o catálogo em PDF.");
    return;
  }
  const cards = products.map((product) => `
    <article>
      ${product.photo ? `<img src="${product.photo}" alt="">` : `<div class="placeholder">Sem foto</div>`}
      <h2>${escapeHtml(product.name)}</h2>
      <small>${escapeHtml(product.barcode || "-")}</small>
      <p>${escapeHtml(product.size || "-")} | ${escapeHtml(product.color || "-")} | ${escapeHtml(product.brand || "-")}</p>
      <strong>${money.format(product.price || 0)}</strong>
      <span>Estoque ${product.stock || 0}</span>
    </article>
  `).join("");
  printWindow.document.write(`
    <!doctype html>
    <html lang="pt-BR">
    <head>
      <meta charset="utf-8">
      <title>Catálogo Mova Sports</title>
      <style>
        body { margin: 0; padding: 28px; font-family: Arial, sans-serif; color: #17212f; }
        header { display: flex; justify-content: space-between; gap: 20px; align-items: center; margin-bottom: 24px; }
        h1 { margin: 0; font-size: 26px; }
        header p { margin: 6px 0 0; color: #66758a; font-weight: 700; }
        .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
        article { break-inside: avoid; border: 1px solid #d7e0ea; border-radius: 10px; padding: 12px; }
        img, .placeholder { width: 100%; aspect-ratio: 1 / 1; object-fit: cover; border-radius: 8px; background: #f4f6f9; display: grid; place-items: center; color: #66758a; font-weight: 700; }
        h2 { margin: 12px 0 4px; font-size: 16px; }
        small, p { color: #66758a; font-weight: 700; }
        p { margin: 8px 0 12px; }
        strong { display: block; font-size: 18px; margin-bottom: 10px; }
        span { display: block; padding: 8px; border-radius: 7px; background: #eaf8ef; color: #159655; font-weight: 900; }
        @media print { body { padding: 18px; } }
      </style>
    </head>
    <body>
      <header><div><h1>Catálogo de produtos</h1><p>Mova Sports</p></div><strong>${products.length} produto${products.length === 1 ? "" : "s"}</strong></header>
      <main class="grid">${cards || "<p>Nenhum produto encontrado.</p>"}</main>
      <script>window.addEventListener("load", () => window.print());<\/script>
    </body>
    </html>
  `);
  printWindow.document.close();
}

function renderStock() {
  const query = normalize(els.stockSearch.value);
  const category = els.stockCategoryFilter.value;
  const brand = els.stockBrandFilter.value;
  const status = els.stockStatusFilter.value;
  const products = db.products.filter((product) => {
    const productStatus = stockStatus(product).key;
    const matchesQuery = !query || normalize(product.name).includes(query) || normalize(product.barcode).includes(query);
    const matchesCategory = category === "all" || product.category === category;
    const matchesBrand = brand === "all" || product.brand === brand;
    const matchesStatus = status === "all" || productStatus === status;
    return matchesQuery && matchesCategory && matchesBrand && matchesStatus;
  });
  els.stockList.innerHTML = "";
  if (!products.length) {
    els.stockList.innerHTML = `<tr><td colspan="10" class="empty-cell">Nenhum produto encontrado.</td></tr>`;
    els.stockFooter.textContent = "Mostrando 0 produtos";
    return;
  }
  products.forEach((product) => {
    const statusInfo = stockStatus(product);
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${escapeHtml(product.barcode || "-")}</td>
      <td>
        <div class="stock-product-cell">
          ${product.photo ? `<img src="${product.photo}" alt="">` : `<div class="stock-product-photo"></div>`}
          <div><strong>${escapeHtml(product.name || "-")}</strong><small>Estoque ${product.stock || 0}</small></div>
        </div>
      </td>
      <td>${escapeHtml(product.category || "-")}</td>
      <td>${escapeHtml(product.brand || "-")}</td>
      <td>${escapeHtml(product.size || "-")}</td>
      <td>${escapeHtml(product.color || "-")}</td>
      <td><span class="stock-badge ${statusInfo.key}"><strong>${product.stock || 0}</strong><small>${statusInfo.label}</small></span></td>
      <td>${money.format(product.cost || 0)}</td>
      <td>${money.format(product.price || 0)}</td>
      <td><div class="table-actions"></div></td>
    `;
    row.querySelector(".table-actions").append(button("...", "stock-menu-button", () => editProduct(product.id)));
    els.stockList.append(row);
  });
  els.stockFooter.innerHTML = `
    <span>Mostrando 1 a ${products.length} de ${products.length} produto${products.length === 1 ? "" : "s"}</span>
    <div class="stock-pagination"><button type="button" disabled>Anterior</button><button type="button" class="active">1</button><button type="button" disabled>Próximo</button></div>
  `;
}

function stockStatus(product) {
  if ((product.stock || 0) <= 0) return { key: "empty", label: "Sem estoque" };
  if ((product.stock || 0) <= (product.minStock || 0)) return { key: "low", label: "Estoque baixo" };
  return { key: "ok", label: "Em estoque" };
}

function renderSaleProducts() {
  const query = normalize(els.saleProductSearch.value);
  const products = db.products.filter((product) => !query || normalize(product.name).startsWith(query) || normalize(product.barcode).includes(query));
  els.saleProductList.innerHTML = "";
  els.saleProductList.classList.toggle("empty", products.length === 0);
  if (!products.length) {
    els.saleProductList.textContent = "Nenhum produto encontrado.";
    return;
  }
  products.slice(0, 8).forEach((product) => {
    const row = document.createElement("article");
    row.className = "sale-product-row";
    row.innerHTML = `
      ${product.photo ? `<img src="${product.photo}" alt="">` : `<div class="sale-product-photo"></div>`}
      <div><strong>${escapeHtml(product.name)}</strong><small>${escapeHtml(product.barcode)} | Estoque: ${product.stock}</small></div>
      <strong>${money.format(product.price)}</strong>
      <div class="table-actions"></div>
    `;
    row.querySelector(".table-actions").append(button("Adicionar", "sale-add-product", () => addToCart(product.id), product.stock <= cartQty(product.id)));
    els.saleProductList.append(row);
  });
}

function addToCart(productId) {
  const product = db.products.find((item) => item.id === productId);
  if (!product || product.stock <= cartQty(product.id)) return alert("Produto sem estoque.");
  const existing = cart.find((item) => item.productId === product.id);
  if (existing) existing.quantity += 1;
  else cart.push({ productId: product.id, barcode: product.barcode, name: product.name, brand: product.brand, quantity: 1, unitCost: product.cost, unitPrice: product.price });
  renderAll();
}

function cartQty(productId) {
  return cart.find((item) => item.productId === productId)?.quantity || 0;
}

function changeCartQty(productId, delta) {
  const item = cart.find((entry) => entry.productId === productId);
  const product = db.products.find((entry) => entry.id === productId);
  if (!item || !product) return;
  item.quantity += delta;
  if (item.quantity <= 0) cart = cart.filter((entry) => entry.productId !== productId);
  if (item.quantity > product.stock) item.quantity = product.stock;
  renderAll();
}

function renderCart() {
  els.cartList.innerHTML = "";
  els.cartList.classList.toggle("empty", cart.length === 0);
  if (!cart.length) {
    els.cartList.innerHTML = `<div class="sale-cart-empty"><span>▢</span><strong>Nenhum item adicionado</strong><small>Adicione produtos para iniciar a venda</small></div>`;
  }
  cart.forEach((item) => {
    const row = document.createElement("article");
    row.className = "sale-cart-row";
    row.innerHTML = `
      <span>${cart.indexOf(item) + 1}</span>
      <strong>${escapeHtml(item.name)}</strong>
      <span>${item.quantity}</span>
      <span>${money.format(item.unitPrice)}</span>
      <b>${money.format(item.quantity * item.unitPrice)}</b>
    `;
    const actions = document.createElement("div");
    actions.className = "sale-cart-actions";
    actions.append(button("+", "ghost", () => changeCartQty(item.productId, 1)));
    actions.append(button("-", "danger", () => changeCartQty(item.productId, -1)));
    row.append(actions);
    els.cartList.append(row);
  });
  if (!els.paymentRows.children.length) addPaymentRow("cash", false);
  const paymentRow = els.paymentRows.querySelectorAll(".payment-row");
  if (paymentRow.length === 1) {
    paymentRow[0].querySelector(".pay-amount").value = fixed(saleTotal());
  }
  renderCartTotalOnly();
}

function addPaymentRow(method = "cash", rerender = true) {
  const row = document.createElement("div");
  row.className = "payment-row";
  row.innerHTML = `
    <label class="field">Forma<select class="pay-method"><option value="cash">Dinheiro</option><option value="pix">PIX</option><option value="debit">Débito</option><option value="credit">Crédito</option><option value="storeCredit">Crediário</option></select></label>
    <label class="field">Valor<input class="pay-amount" type="number" min="0.01" step="0.01"></label>
    <button class="danger remove-pay" type="button">X</button>
  `;
  row.querySelector(".pay-method").value = method;
  row.querySelector(".pay-amount").value = fixed(saleTotal());
  row.addEventListener("input", renderCartTotalOnly);
  row.querySelector(".remove-pay").addEventListener("click", () => {
    row.remove();
    renderCartTotalOnly();
  });
  els.paymentRows.append(row);
  if (rerender) renderCartTotalOnly();
}

function renderCartTotalOnly() {
  els.saleTotal.textContent = money.format(saleTotal());
  if (els.saleChange) {
    const paid = readPayments().reduce((total, payment) => total + payment.amount, 0);
    els.saleChange.textContent = money.format(Math.max(0, round(paid - saleTotal())));
  }
}

function readPayments() {
  return [...els.paymentRows.querySelectorAll(".payment-row")].map((row) => ({
    method: row.querySelector(".pay-method").value,
    amount: readNumber(row.querySelector(".pay-amount").value),
  })).filter((payment) => payment.amount > 0);
}

function saleSubtotal() {
  return cart.reduce((total, item) => total + item.quantity * item.unitPrice, 0);
}

function saleTotal() {
  return Math.max(0, round(saleSubtotal() - readNumber(els.saleDiscount.value)));
}

async function finishSale() {
  if (!cart.length) return alert("Adicione produtos.");
  const total = saleTotal();
  const payments = readPayments();
  if (Math.abs(sum(payments, "amount") - total) > 0.01) return alert("Pagamentos precisam fechar com o total.");
  const customer = findCustomerByName(els.saleCustomerSearch.value.trim());
  const storeCredit = payments.filter((payment) => payment.method === "storeCredit").reduce((value, payment) => value + payment.amount, 0);
  if (storeCredit > 0 && !customer) return alert("Crediário exige cliente cadastrado.");
  if (storeCredit > 0 && customer) {
    const open = customerDebt(customer.id).open;
    if (open + storeCredit > customer.limit) {
      if (!isAdmin()) return alert("Limite de crédito ultrapassado. Apenas admin pode liberar.");
      if (!confirm("Limite ultrapassado. Admin deseja liberar a venda?")) return;
    }
  }
  const sale = {
    id: nextSaleCode(),
    customerId: customer?.id || "",
    customerName: customer?.name || "Venda simples",
    items: cart.map((item) => ({ ...item, total: item.quantity * item.unitPrice })),
    subtotal: saleSubtotal(),
    discount: readNumber(els.saleDiscount.value),
    total,
    costTotal: cart.reduce((value, item) => value + item.quantity * item.unitCost, 0),
    payments,
    status: "completed",
    createdAt: new Date().toISOString(),
  };

  if (BACKEND_ENABLED) {
    try {
      const response = await fetch("/api/sales", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...sale, storeCreditInstallments: Math.max(1, Math.floor(readNumber(els.storeCreditInstallments.value))) }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        alert(payload.error || "Não foi possível finalizar a venda.");
        return;
      }
      applySaleResultLocally(payload.data);
      persistLocalOnly();
      showReceipt(payload.data.sale);
      clearSale();
      renderAll();
      return;
    } catch (error) {
      console.warn(error);
      alert("Não foi possível conectar ao servidor para finalizar a venda.");
      return;
    }
  }

  sale.items.forEach((item) => {
    const product = db.products.find((entry) => entry.id === item.productId);
    product.stock -= item.quantity;
  });
  db.sales.unshift(sale);
  createFinancialFromSale(sale, customer, storeCredit);
  persist();
  showReceipt(sale);
  clearSale();
  renderAll();
}

function applySaleResultLocally(result) {
  if (!result?.sale) return;
  const products = result.products || [];
  const productsById = new Map(products.map((product) => [product.id, product]));
  db.products = db.products.map((product) => productsById.get(product.id) || product);
  products.forEach((product) => {
    if (!db.products.some((item) => item.id === product.id)) db.products.push(product);
  });
  db.sales = [result.sale, ...db.sales.filter((sale) => sale.id !== result.sale.id)];
  db.cash = [...(result.cash || []), ...db.cash];
  db.receivables = [...(result.receivables || []), ...db.receivables];
}

function createFinancialFromSale(sale, customer, storeCredit) {
  sale.payments.forEach((payment) => {
    if (payment.method === "cash" || payment.method === "pix") {
      addCash("in", "sale", `Venda ${sale.id}`, payment.method, payment.amount, sale.id);
    }
    if (payment.method === "debit" || payment.method === "credit") {
      db.receivables.push({ id: createId(), saleId: sale.id, customerId: sale.customerId, customerName: sale.customerName, method: payment.method, amount: payment.amount, received: 0, status: "cardPending", dueDate: todayIso, createdAt: sale.createdAt });
    }
    if (payment.method === "storeCredit") {
      const installments = Math.max(1, Math.floor(readNumber(els.storeCreditInstallments.value)));
      const part = round(payment.amount / installments);
      for (let index = 1; index <= installments; index += 1) {
        const due = new Date(sale.createdAt);
        due.setDate(due.getDate() + 30 * index);
        db.receivables.push({ id: createId(), saleId: sale.id, customerId: customer.id, customerName: customer.name, method: "storeCredit", amount: index === installments ? round(payment.amount - part * (installments - 1)) : part, received: 0, status: "open", dueDate: toDateInput(due), createdAt: sale.createdAt });
      }
    }
  });
}

function clearSale() {
  cart = [];
  els.saleCustomerSearch.value = "";
  els.saleDiscount.value = "0";
  els.paymentRows.innerHTML = "";
  addPaymentRow("cash", false);
  renderAll();
}

function showReceipt(sale) {
  els.receiptPanel.hidden = false;
  els.receiptPanel.innerHTML = `
    <div class="section-title"><h2>Comprovante venda ${sale.id}</h2><button id="printCurrentReceiptButton" class="primary" type="button">Imprimir</button></div>
    ${saleReceiptMarkup(sale)}
  `;
  els.receiptPanel.querySelector("#printCurrentReceiptButton").addEventListener("click", () => openSaleReceiptPrint(sale));
}

function saleReceiptMarkup(sale) {
  const items = (sale.items || []).map((item) => `
    <p>${Number(item.quantity || 0)}x ${escapeHtml(item.name)} - ${money.format(item.total || (Number(item.quantity || 0) * Number(item.unitPrice || 0)))}</p>
  `).join("");
  const payments = (sale.payments || []).map((payment) => `${paymentLabels[payment.method] || payment.method}: ${money.format(payment.amount || 0)}`).join(" | ");
  return `
    <div class="receipt">
      <h3>Mova Sports</h3>
      <p><strong>Venda:</strong> ${escapeHtml(sale.id)}</p>
      <p><strong>Cliente:</strong> ${escapeHtml(sale.customerName || "Venda simples")}</p>
      <p><strong>Data:</strong> ${formatDateTime(sale.createdAt)}</p>
      <hr>
      ${items || "<p>Nenhum item registrado.</p>"}
      <hr>
      <p>Subtotal: ${money.format(sale.subtotal || 0)}</p>
      <p>Desconto: ${money.format(sale.discount || 0)}</p>
      <strong>Total: ${money.format(sale.total || 0)}</strong>
      <p>${escapeHtml(payments || "-")}</p>
    </div>
  `;
}

function openSaleReceiptPrint(sale) {
  const printWindow = window.open("", "_blank");
  if (!printWindow) {
    alert("Permita pop-ups para imprimir o comprovante.");
    return;
  }
  printWindow.document.write(`
    <!doctype html>
    <html lang="pt-BR">
    <head>
      <meta charset="utf-8">
      <title>Comprovante ${escapeHtml(sale.id)}</title>
      <style>
        body { margin: 0; padding: 24px; font-family: Arial, sans-serif; color: #17212f; background: #fff; }
        .receipt { width: 360px; max-width: 100%; margin: 0 auto; padding: 16px; border: 1px dashed #aeb9c8; border-radius: 8px; }
        h3 { margin: 0 0 12px; text-align: center; font-size: 20px; }
        p { margin: 7px 0; font-size: 14px; }
        strong { font-size: 17px; }
        hr { border: 0; border-top: 1px dashed #cfd7e2; margin: 12px 0; }
        @media print { body { padding: 0; } .receipt { border: 0; } }
      </style>
    </head>
    <body>
      ${saleReceiptMarkup(sale)}
      <script>window.addEventListener("load", () => window.print());<\/script>
    </body>
    </html>
  `);
  printWindow.document.close();
}

async function registerReturn(event) {
  event.preventDefault();
  const sale = findSaleByCode(els.returnProductSearch.value);
  if (!sale) return alert("Venda não encontrada.");
  const items = readReturnItems(sale);
  if (!items.length) return alert("Informe a quantidade de pelo menos um item para devolver.");
  const returnDoc = {
    id: createId(),
    saleId: sale.id,
    customerName: sale.customerName,
    items,
    total: items.reduce((total, item) => total + item.total, 0),
    reason: els.returnReason.value.trim(),
    notes: els.returnNotes?.value.trim() || "",
    createdAt: new Date().toISOString(),
  };
  if (BACKEND_ENABLED) {
    try {
      const response = await fetch("/api/returns", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(returnDoc),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        alert(payload.error || "Não foi possível registrar a devolução/troca.");
        return;
      }
      applyReturnResultLocally(payload.data);
      persistLocalOnly();
      els.returnForm.reset();
      renderAll();
      return;
    } catch (error) {
      console.warn(error);
      alert("Não foi possível conectar ao servidor para registrar a devolução/troca.");
      return;
    }
  }
  items.forEach((item) => {
    const product = db.products.find((entry) => entry.id === item.productId);
    if (product) product.stock += item.quantity;
  });
  db.returns.unshift(returnDoc);
  persist();
  els.returnForm.reset();
  renderAll();
}

function applyReturnResultLocally(result) {
  if (!result?.return) return;
  const products = result.products || [];
  const productsById = new Map(products.map((product) => [product.id, product]));
  db.products = db.products.map((product) => productsById.get(product.id) || product);
  products.forEach((product) => {
    if (!db.products.some((item) => item.id === product.id)) db.products.push(product);
  });
  db.returns = [result.return, ...db.returns.filter((item) => item.id !== result.return.id)];
}

function renderReturnSaleItems() {
  if (!els.returnItemsList) return;
  const sale = findSaleByCode(els.returnProductSearch.value);
  if (!els.returnProductSearch.value.trim()) {
    els.returnItemsList.className = "return-empty";
    els.returnItemsList.innerHTML = `<span>□</span><strong>Nenhuma venda selecionada</strong><small>Busque uma venda para visualizar os itens.</small>`;
    updateReturnSummary(0);
    return;
  }
  if (!sale) {
    els.returnItemsList.className = "return-empty";
    els.returnItemsList.innerHTML = `<span>!</span><strong>Venda não encontrada</strong><small>Confira o número da venda e tente novamente.</small>`;
    updateReturnSummary(0);
    return;
  }
  els.returnItemsList.className = "return-items-list";
  els.returnItemsList.innerHTML = sale.items.map((item, index) => {
    const product = db.products.find((entry) => entry.id === item.productId);
    const variation = [product?.size, product?.color].filter(Boolean).join(" / ") || "-";
    return `
      <div class="return-item-row" data-index="${index}">
        <span><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.barcode || "")}</small></span>
        <span>${escapeHtml(variation)}</span>
        <span>${item.quantity}</span>
        <select class="return-action"><option value="">Não incluir</option><option value="return">Devolver</option><option value="exchange">Trocar</option></select>
        <input class="return-qty" type="number" min="0" max="${item.quantity}" step="1" value="0" disabled>
        <span>${money.format(item.unitPrice)}</span>
        <b>${money.format(0)}</b>
      </div>
    `;
  }).join("");
  els.returnItemsList.querySelectorAll(".return-action, .return-qty").forEach((input) => input.addEventListener("input", () => updateReturnRows(sale)));
  updateReturnRows(sale);
}

function updateReturnRows(sale) {
  let total = 0;
  els.returnItemsList.querySelectorAll(".return-item-row").forEach((row) => {
    const item = sale.items[Number(row.dataset.index)];
    const action = row.querySelector(".return-action").value;
    const input = row.querySelector(".return-qty");
    input.disabled = !action;
    const quantity = action ? Math.min(item.quantity, Math.max(0, Math.floor(readNumber(input.value)))) : 0;
    input.value = quantity ? String(quantity) : "0";
    const value = round(quantity * item.unitPrice);
    row.querySelector("b").textContent = money.format(value);
    total += value;
  });
  updateReturnSummary(total);
}

function updateReturnSummary(total) {
  if (els.returnTotalLabel) els.returnTotalLabel.textContent = money.format(total);
  if (els.returnRefundLabel) els.returnRefundLabel.textContent = money.format(total);
}

function readReturnItems(sale) {
  return [...els.returnItemsList.querySelectorAll(".return-item-row")].map((row) => {
    const item = sale.items[Number(row.dataset.index)];
    const action = row.querySelector(".return-action").value;
    const quantity = action ? Math.min(item.quantity, Math.max(0, Math.floor(readNumber(row.querySelector(".return-qty").value)))) : 0;
    return {
      productId: item.productId,
      productName: item.name,
      action,
      quantity,
      unitPrice: item.unitPrice,
      total: round(quantity * item.unitPrice),
    };
  }).filter((item) => item.action && item.quantity > 0);
}

function findSaleByCode(value) {
  const query = normalize(value);
  if (!query) return null;
  return db.sales.find((sale) => normalize(sale.id) === query) || db.sales.find((sale) => normalize(sale.id).startsWith(query));
}

function renderSaleHistory() {
  if (!els.saleHistoryClients || !els.saleHistorySales) return;
  const query = normalize(els.saleHistorySearch.value || "");
  const groups = saleHistoryGroups().filter((group) => !query || normalize(group.name).includes(query));
  if (!groups.some((group) => group.key === selectedSaleHistoryKey)) selectedSaleHistoryKey = groups[0]?.key || "";
  els.saleHistoryClients.classList.toggle("empty", groups.length === 0);
  els.saleHistoryClients.innerHTML = "";
  if (!groups.length) {
    els.saleHistoryClients.textContent = "Nenhum cliente encontrado.";
    renderSaleHistoryDetail(null);
    return;
  }
  groups.forEach((group) => {
    const item = document.createElement("button");
    item.type = "button";
    item.className = `sale-history-client${group.key === selectedSaleHistoryKey ? " active" : ""}`;
    item.innerHTML = `
      <span>${escapeHtml(group.initials)}</span>
      <div>
        <strong>${escapeHtml(group.name)}</strong>
        <small>${group.sales.length} compra${group.sales.length === 1 ? "" : "s"} | ${money.format(group.total)}</small>
      </div>
    `;
    item.addEventListener("click", () => {
      selectedSaleHistoryKey = group.key;
      renderSaleHistory();
    });
    els.saleHistoryClients.append(item);
  });
  renderSaleHistoryDetail(groups.find((group) => group.key === selectedSaleHistoryKey));
}

function saleHistoryGroups() {
  const groups = db.customers.map((customer) => {
    const sales = db.sales.filter((sale) => sale.customerId === customer.id).sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    const receivables = db.receivables.filter((item) => item.customerId === customer.id).sort((a, b) => String(b.createdAt || "").localeCompare(String(a.createdAt || "")));
    return saleHistoryGroupFromData(`customer:${customer.id}`, customer.name, sales, receivables);
  }).filter((group) => group.sales.length || group.receivables.length);
  const simpleSales = db.sales.filter((sale) => !sale.customerId).sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  if (simpleSales.length) groups.unshift(saleHistoryGroupFromData("simple", "Venda simples", simpleSales, []));
  return groups.sort((a, b) => {
    if (a.key === "simple") return -1;
    if (b.key === "simple") return 1;
    return a.name.localeCompare(b.name, "pt-BR");
  });
}

function saleHistoryGroupFromData(key, name, sales, receivables) {
  const activeSales = sales.filter((sale) => sale.status !== "cancelled");
  const total = activeSales.reduce((value, sale) => value + Number(sale.total || 0), 0);
  const paidInSales = activeSales.flatMap((sale) => sale.payments || [])
    .filter((payment) => payment.method !== "storeCredit")
    .reduce((value, payment) => value + Number(payment.amount || 0), 0);
  const paidReceivables = receivables.reduce((value, item) => value + Number(item.received || 0), 0);
  const open = receivables.filter((item) => item.status !== "cancelled").reduce((value, item) => value + receivableBalance(item), 0);
  return {
    key,
    name,
    initials: initialsFromName(name),
    sales,
    receivables,
    total,
    paid: paidInSales + paidReceivables,
    open,
  };
}

function renderSaleHistoryDetail(group) {
  if (!group) {
    els.saleHistorySummary.className = "sale-history-summary empty";
    els.saleHistorySummary.innerHTML = "<strong>Selecione um cliente</strong><span>As compras e pagamentos aparecerão aqui.</span>";
    els.saleHistorySales.className = "sale-history-sales empty";
    els.saleHistorySales.textContent = "Nenhuma venda selecionada.";
    return;
  }
  els.saleHistorySummary.className = "sale-history-summary";
  els.saleHistorySummary.innerHTML = `
    <article><span>Cliente</span><strong>${escapeHtml(group.name)}</strong></article>
    <article><span>Total comprado</span><strong>${money.format(group.total)}</strong></article>
    <article><span>Total pago</span><strong>${money.format(group.paid)}</strong></article>
    <article><span>Saldo em aberto</span><strong>${money.format(group.open)}</strong></article>
  `;
  els.saleHistorySales.className = "sale-history-sales";
  els.saleHistorySales.innerHTML = group.sales.length
    ? group.sales.map((sale) => saleHistorySaleCard(sale, group.receivables.filter((item) => item.saleId === sale.id))).join("")
    : `<div class="sale-history-empty">Nenhuma compra encontrada para este cliente.</div>`;
  els.saleHistorySales.querySelectorAll(".sale-history-print").forEach((buttonEl) => {
    buttonEl.addEventListener("click", () => {
      const sale = db.sales.find((item) => item.id === buttonEl.dataset.saleId);
      if (sale) openSaleReceiptPrint(sale);
    });
  });
}

function saleHistorySaleCard(sale, receivables) {
  const items = (sale.items || []).map((item) => `${item.quantity}x ${item.name}`).join(", ") || "-";
  const payments = (sale.payments || []).map((payment) => `${paymentLabels[payment.method] || payment.method}: ${money.format(payment.amount || 0)}`).join(" | ") || "-";
  const receivableRows = receivables.length
    ? receivables.flatMap((item) => {
      const paid = Number(item.received || 0);
      const balance = receivableBalance(item);
      const header = `<li><strong>Parcela ${escapeHtml(item.installment || "-")}</strong> | Venc. ${formatDate(item.dueDate)} | Pago ${money.format(paid)} | Aberto ${money.format(balance)}</li>`;
      const paymentRows = receivablePaymentRows(item).map((payment) => `<li class="sale-history-payment">Pagamento ${formatDateTime(payment.createdAt)} | ${escapeHtml(paymentLabels[payment.method] || payment.method || "Recebimento")} | ${money.format(payment.amount || 0)}</li>`);
      return [header, ...paymentRows];
    }).join("")
    : "<li>Sem parcelas vinculadas.</li>";
  return `
    <article class="sale-history-sale ${sale.status === "cancelled" ? "cancelled" : ""}">
      <div class="sale-history-sale-head">
        <div>
          <strong>Venda ${escapeHtml(sale.id)}</strong>
          <small>${formatDateTime(sale.createdAt)} | ${sale.status === "cancelled" ? "Cancelada" : "Concluída"}</small>
        </div>
        <div class="sale-history-sale-actions">
          <b>${money.format(sale.total || 0)}</b>
          <button class="ghost sale-history-print" type="button" data-sale-id="${escapeHtml(sale.id)}">Comprovante</button>
        </div>
      </div>
      <p><strong>Itens:</strong> ${escapeHtml(items)}</p>
      <p><strong>Pagamentos:</strong> ${escapeHtml(payments)}</p>
      <ul>${receivableRows}</ul>
    </article>
  `;
}

function receivablePaymentRows(receivable) {
  const payments = Array.isArray(receivable.payments) ? receivable.payments : [];
  if (payments.length) return payments.slice().sort((a, b) => String(a.createdAt || "").localeCompare(String(b.createdAt || "")));
  if (Number(receivable.received || 0) > 0) {
    return [{
      method: receivable.method,
      amount: Number(receivable.received || 0),
      createdAt: receivable.lastPaymentAt || receivable.paidAt || receivable.updatedAt || receivable.createdAt,
    }];
  }
  return [];
}

function initialsFromName(name) {
  const parts = String(name || "VS").trim().split(/\s+/).filter(Boolean);
  return (parts.length > 1 ? `${parts[0][0]}${parts[parts.length - 1][0]}` : (parts[0] || "VS").slice(0, 2)).toUpperCase();
}

function renderCustomerReceivable(customer, container) {
  const debt = customerDebt(customer.id);
  const row = tableRow(customer.name, `Aberto ${money.format(debt.open)} | Limite ${money.format(customer.limit)}`, "");
  const actions = document.createElement("div");
  actions.className = "row-actions";
  actions.append(button("Receber parcela", "primary", () => receiveCustomerDebt(customer.id), debt.open <= 0));
  row.append(actions);
  container.append(row);
}

function receiveCustomerDebt(customerId) {
  const debt = customerDebt(customerId).open;
  const amount = readNumber(prompt("Valor recebido", fixed(debt)));
  if (amount <= 0 || amount > debt) return alert("Valor invalido.");
  const method = normalizePayment(prompt("Forma: dinheiro, pix, débito ou crédito", "pix"));
  let remaining = amount;
  db.receivables.filter((item) => item.customerId === customerId && item.method === "storeCredit" && receivableBalance(item) > 0).sort((a, b) => a.dueDate.localeCompare(b.dueDate)).forEach((item) => {
    if (remaining <= 0) return;
    const paid = Math.min(receivableBalance(item), remaining);
    item.received += paid;
    item.status = receivableBalance(item) <= 0.01 ? "paid" : "open";
    remaining = round(remaining - paid);
  });
  if (method === "cash" || method === "pix") addCash("in", "crediario", "Recebimento crediario", method, amount, customerId);
  if (method === "debit" || method === "credit") db.receivables.push({ id: createId(), customerId, method, amount, received: 0, status: "cardPending", dueDate: todayIso, createdAt: new Date().toISOString() });
  persist();
  renderAll();
}

function renderManualReceiptSummary() {
  if (!els.manualCreditSummary) return;
  const credit = readNumber(els.manualCreditAmount.value);
  const debit = readNumber(els.manualDebitAmount.value);
  els.manualCreditSummary.textContent = money.format(credit);
  els.manualDebitSummary.textContent = money.format(debit);
  els.manualReceiptTotal.textContent = money.format(credit + debit);
}

async function saveManualReceipt(event) {
  event.preventDefault();
  const credit = readNumber(els.manualCreditAmount.value);
  const debit = readNumber(els.manualDebitAmount.value);
  const total = round(credit + debit);
  if (total <= 0) return alert("Informe um valor de crédito ou débito.");
  const description = els.manualReceiptDescription.value.trim() || "Recebimento manual de cartão";
  const createdAt = timestampForDateInput(els.manualReceiptDate.value || todayIso);
  if (BACKEND_ENABLED) {
    try {
      const response = await fetch("/api/card-receipts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ credit, debit, description, createdAt, type: "recebimento cartão" }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        alert(payload.error || "Não foi possível registrar o recebimento.");
        return;
      }
      applyCashResultLocally(payload.data);
      persistLocalOnly();
      els.manualReceiptForm.reset();
      els.manualReceiptDate.value = todayIso;
      renderManualReceiptSummary();
      renderAll();
      return;
    } catch (error) {
      console.warn(error);
      alert("Não foi possível conectar ao servidor para registrar o recebimento.");
      return;
    }
  }
  if (credit > 0) addCash("in", "recebimento cartão", `${description} - Crédito`, "card", credit, "", createdAt);
  if (debit > 0) addCash("in", "recebimento cartão", `${description} - Débito`, "card", debit, "", createdAt);
  settleCardPending(total, createdAt);
  persist();
  els.manualReceiptForm.reset();
  els.manualReceiptDate.value = todayIso;
  renderManualReceiptSummary();
  renderAll();
}

function applyCashResultLocally(result) {
  db.cash = [...(result?.cash || []), ...db.cash];
  (result?.receivables || []).forEach((updated) => {
    db.receivables = db.receivables.map((item) => item.id === updated.id ? updated : item);
  });
}

function applyPayableLocally(payable) {
  if (!payable) return;
  const index = db.payables.findIndex((item) => item.id === payable.id);
  if (index >= 0) {
    db.payables[index] = payable;
  } else {
    db.payables.push(payable);
  }
}

function applyPayablePaymentResultLocally(result) {
  applyPayableLocally(result?.payable);
  db.cash = [...(result?.cash || []), ...db.cash];
}

function settleCardPending(amount, paidAt = new Date().toISOString()) {
  let remaining = amount;
  db.receivables.filter((item) => item.status === "cardPending").sort((a, b) => a.createdAt.localeCompare(b.createdAt)).forEach((item) => {
    if (remaining <= 0) return;
    const paid = Math.min(item.amount - item.received, remaining);
    item.received += paid;
    item.lastPaymentAt = paidAt;
    item.payments = [...(item.payments || []), { id: createId(), method: "card", amount: paid, createdAt: item.lastPaymentAt }];
    if (item.amount - item.received <= 0.01) item.status = "paid";
    remaining = round(remaining - paid);
  });
}

function renderCancelSales() {
  const start = els.cancelSaleDate.value || todayIso;
  const end = els.cancelSaleEndDate.value || start;
  const startDate = start <= end ? start : end;
  const endDate = end >= start ? end : start;
  const query = normalize(els.cancelSaleSearch.value);
  const sales = db.sales
    .filter((sale) => {
      const saleDate = sale.createdAt.slice(0, 10);
      if (saleDate < startDate || saleDate > endDate) return false;
      if (!query) return true;
      const customer = db.customers.find((item) => item.id === sale.customerId);
      const searchable = [
        sale.id,
        sale.customerName,
        customer?.cpf,
        ...(sale.items || []).map((item) => item.name)
      ].join(" ");
      return normalize(searchable).includes(query);
    })
    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  els.cancelSaleList.innerHTML = "";
  els.cancelSaleFooter.innerHTML = "";
  els.cancelSaleList.classList.toggle("empty", sales.length === 0);
  if (!sales.length) {
    els.cancelSaleList.textContent = "Nenhuma venda encontrada.";
    return;
  }
  sales.forEach((sale) => {
    const row = document.createElement("article");
    const items = (sale.items || []).map((item) => `${item.quantity}x ${item.name}`).join(", ");
    const saleDate = sale.createdAt.slice(0, 10);
    const saleTime = new Date(sale.createdAt).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
    const isCancelled = sale.status === "cancelled";
    row.className = `cancel-sale-row${isCancelled ? " is-cancelled" : ""}`;
    row.innerHTML = `
      <div class="cancel-sale-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M6 6h15l-2 8H8L6 3H3"/><circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/></svg></div>
      <div class="cancel-sale-main">
        <strong>Venda ${escapeHtml(sale.id)}</strong>
        <small>Cliente: ${escapeHtml(sale.customerName || "Venda simples")}</small>
        <small>${escapeHtml(items || "Sem itens registrados")}</small>
      </div>
      <div class="cancel-sale-date">
        <span>${formatDate(saleDate)} - ${saleTime}</span>
        <em>${isCancelled ? "Cancelada" : "Conclu&iacute;da"}</em>
      </div>
      <strong class="cancel-sale-total">${money.format(sale.total || 0)}</strong>
    `;
    const actions = document.createElement("div");
    actions.className = "cancel-sale-actions";
    actions.append(button("Cancelar venda", "danger cancel-sale-button", () => cancelSale(sale.id), isCancelled));
    row.append(actions);
    els.cancelSaleList.append(row);
  });
  els.cancelSaleFooter.innerHTML = `
    <span>Mostrando 1 a ${sales.length} de ${sales.length} venda${sales.length === 1 ? "" : "s"}</span>
    <div class="cancel-pagination">
      <button type="button" disabled>Anterior</button>
      <button type="button" class="active">1</button>
      <button type="button" disabled>Próximo</button>
    </div>
  `;
}

async function cancelSale(saleId) {
  const sale = db.sales.find((item) => item.id === saleId);
  if (!sale || !confirm("Cancelar venda e voltar estoque?")) return;
  if (BACKEND_ENABLED) {
    try {
      const response = await fetch(`/api/sales/${encodeURIComponent(saleId)}/cancel`, { method: "POST" });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        alert(payload.error || "Não foi possível cancelar a venda.");
        return;
      }
      applyCancelSaleResultLocally(payload.data);
      persistLocalOnly();
      renderAll();
      return;
    } catch (error) {
      console.warn(error);
      alert("Não foi possível conectar ao servidor para cancelar a venda.");
      return;
    }
  }
  sale.status = "cancelled";
  sale.items.forEach((item) => {
    const product = db.products.find((entry) => entry.id === item.productId);
    if (product) product.stock += item.quantity;
  });
  db.receivables.forEach((item) => {
    if (item.saleId === saleId) item.status = "cancelled";
  });
  addCash("out", "cancelamento", `Cancelamento venda ${sale.id}`, "cash", sale.payments.filter((payment) => payment.method === "cash").reduce((total, payment) => total + payment.amount, 0), sale.id);
  persist();
  renderAll();
}

function applyCancelSaleResultLocally(result) {
  if (!result?.sale) return;
  db.sales = db.sales.map((sale) => sale.id === result.sale.id ? { ...sale, ...result.sale, status: "cancelled" } : sale);
  const products = result.products || [];
  const productsById = new Map(products.map((product) => [product.id, product]));
  db.products = db.products.map((product) => productsById.get(product.id) || product);
  db.receivables = db.receivables.map((receivable) => {
    const updated = (result.receivables || []).find((item) => item.id === receivable.id);
    return updated || receivable;
  });
  db.cash = [...(result.cash || []), ...db.cash];
}

function renderCreditCustomers() {
  const query = normalize(els.creditCustomerSearch.value);
  const creditItems = db.receivables.filter((item) => item.method === "storeCredit" && item.status !== "cancelled" && receivableBalance(item) > 0);
  const openTotal = creditItems.reduce((total, item) => total + receivableBalance(item), 0);
  const dueItems = creditItems.filter((item) => item.dueDate >= todayIso);
  const overdueItems = creditItems.filter((item) => item.dueDate < todayIso);
  els.creditOpenTotal.textContent = money.format(openTotal);
  els.creditOpenCount.textContent = `${creditItems.length} parcela${creditItems.length === 1 ? "" : "s"}`;
  els.creditDueTotal.textContent = money.format(dueItems.reduce((total, item) => total + receivableBalance(item), 0));
  els.creditDueCount.textContent = `${dueItems.length} parcela${dueItems.length === 1 ? "" : "s"}`;
  els.creditOverdueTotal.textContent = money.format(overdueItems.reduce((total, item) => total + receivableBalance(item), 0));
  els.creditOverdueCount.textContent = `${overdueItems.length} parcela${overdueItems.length === 1 ? "" : "s"}`;
  const customers = db.customers.filter((customer) => {
    const text = [customer.name, customer.whatsapp, customer.phone, customer.cpf].join(" ");
    return customerCreditStats(customer.id).open > 0 && (!query || normalize(text).includes(query));
  });
  els.creditCustomerList.innerHTML = "";
  els.creditFooter.innerHTML = "";
  if (!customers.length) {
    els.creditCustomerList.innerHTML = `<tr><td colspan="6" class="empty-cell">Nenhum cliente encontrado.</td></tr>`;
    els.creditFooter.textContent = "Mostrando 0 clientes";
    return;
  }
  customers.forEach((customer) => {
    const stats = customerCreditStats(customer.id);
    const row = document.createElement("tr");
    const initials = customer.name.split(" ").filter(Boolean).slice(0, 2).map((part) => part[0]).join("").toUpperCase() || "CL";
    const statusClass = stats.overdueCount > 0 ? "overdue" : "ok";
    row.innerHTML = `
      <td>
        <div class="credit-client-cell">
          <span>${escapeHtml(initials)}</span>
          <div><strong>${escapeHtml(customer.name)}</strong><small>${escapeHtml(customer.whatsapp || "-")} | CPF: ${escapeHtml(customer.cpf || "-")}</small></div>
        </div>
      </td>
      <td>${money.format(customer.creditLimit || 0)}</td>
      <td>${money.format(stats.open)}</td>
      <td><strong>${stats.totalCount} parcela${stats.totalCount === 1 ? "" : "s"}</strong><small>${stats.openCount} em aberto</small></td>
      <td><span class="credit-status ${statusClass}">${stats.overdueCount > 0 ? "Atrasado" : "Em dia"}</span></td>
      <td><div class="credit-actions"></div></td>
    `;
    const actions = row.querySelector(".credit-actions");
    actions.append(button("Receber", "credit-receive-button", () => openCreditReceiveModal(customer.id), stats.open <= 0));
    els.creditCustomerList.append(row);
  });
  els.creditFooter.innerHTML = `
    <span>Mostrando 1 a ${customers.length} de ${customers.length} cliente${customers.length === 1 ? "" : "s"}</span>
    <div class="credit-pagination"><button type="button" disabled>Anterior</button><button type="button" class="active">1</button><button type="button" disabled>Próximo</button></div>
  `;
}

function openCreditReceiveModal(customerId) {
  const customer = db.customers.find((item) => item.id === customerId);
  const items = db.receivables
    .filter((item) => item.customerId === customerId && item.method === "storeCredit" && item.status !== "cancelled" && receivableBalance(item) > 0)
    .sort((a, b) => a.dueDate.localeCompare(b.dueDate));
  if (!customer || !items.length) return alert("Cliente sem parcelas em aberto.");
  els.creditReceiveCustomerId.value = customerId;
  els.creditReceiveCustomerName.textContent = customer.name;
  els.creditReceiveDate.value = todayIso;
  els.creditReceiveMethod.value = "cash";
  els.creditReceiveNote.value = "";
  els.creditReceiveOpenTotal.textContent = money.format(items.reduce((total, item) => total + receivableBalance(item), 0));
  els.creditReceiveList.innerHTML = items.map((item) => {
    const balance = receivableBalance(item);
    const status = item.dueDate < todayIso ? "Atrasada" : "Em aberto";
    return `
      <article class="credit-receive-row" data-id="${escapeHtml(item.id)}">
        <div>
          <strong>Parcela ${escapeHtml(item.installment || "-")} | Venda ${escapeHtml(item.saleId || "-")}</strong>
          <small>Vencimento ${formatDate(item.dueDate)} | ${status}</small>
        </div>
        <span>${money.format(balance)}</span>
        <label>Receber<input class="credit-receive-amount" type="number" min="0" max="${fixed(balance)}" step="0.01" value="${fixed(balance)}"></label>
      </article>
    `;
  }).join("");
  els.creditReceiveModal.hidden = false;
  renderCreditReceiveTotal();
}

function closeCreditReceiveModal() {
  els.creditReceiveModal.hidden = true;
}

function renderCreditReceiveTotal() {
  const total = [...els.creditReceiveList.querySelectorAll(".credit-receive-amount")].reduce((sumValue, input) => sumValue + readNumber(input.value), 0);
  els.creditReceiveTotal.textContent = money.format(total);
}

async function saveCreditReceipt(event) {
  event.preventDefault();
  const customerId = els.creditReceiveCustomerId.value;
  const customer = db.customers.find((item) => item.id === customerId);
  if (!customer) return;
  const rows = [...els.creditReceiveList.querySelectorAll(".credit-receive-row")].map((row) => {
    const receivable = db.receivables.find((item) => item.id === row.dataset.id);
    const amount = round(readNumber(row.querySelector(".credit-receive-amount").value));
    return { receivable, amount };
  }).filter((item) => item.receivable && item.amount > 0);
  const total = round(rows.reduce((sumValue, item) => sumValue + item.amount, 0));
  if (total <= 0) return alert("Informe pelo menos um valor para receber.");
  for (const row of rows) {
    const balance = receivableBalance(row.receivable);
    if (row.amount > balance + 0.01) return alert("Valor recebido maior que o saldo da parcela.");
  }
  const method = els.creditReceiveMethod.value;
  const description = `Recebimento crediário - ${customer.name}${els.creditReceiveNote.value.trim() ? ` - ${els.creditReceiveNote.value.trim()}` : ""}`;
  const createdAt = timestampForDateInput(els.creditReceiveDate.value || todayIso);
  if (BACKEND_ENABLED) {
    try {
      const response = await fetch("/api/receivables/payments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customerId,
          method,
          description,
          createdAt,
          payments: rows.map(({ receivable, amount }) => ({ receivableId: receivable.id, amount })),
        }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        alert(payload.error || "Não foi possível registrar o recebimento.");
        return;
      }
      applyReceivablePaymentResultLocally(payload.data);
      persistLocalOnly();
      closeCreditReceiveModal();
      renderAll();
      return;
    } catch (error) {
      console.warn(error);
      alert("Não foi possível conectar ao servidor para registrar o recebimento.");
      return;
    }
  }
  rows.forEach(({ receivable, amount }) => {
    receivable.received = round((receivable.received || 0) + amount);
    receivable.status = receivableBalance(receivable) <= 0.01 ? "paid" : "open";
    receivable.lastPaymentAt = createdAt;
    receivable.payments = [...(receivable.payments || []), { id: createId(), method: els.creditReceiveMethod.value, amount, createdAt }];
    receivable.paidAt = receivable.status === "paid" ? createdAt : receivable.paidAt;
  });
  if (method === "cash" || method === "pix") addCash("in", "crediario", description, method, total, customerId, createdAt);
  if (method === "debit" || method === "credit") {
    db.receivables.push({ id: createId(), customerId, customerName: customer.name, method, amount: total, received: 0, status: "cardPending", dueDate: els.creditReceiveDate.value || todayIso, createdAt });
  }
  persist();
  closeCreditReceiveModal();
  renderAll();
}

function applyReceivablePaymentResultLocally(result) {
  const updated = result?.receivables || [];
  const existingIds = new Set(db.receivables.map((item) => item.id));
  db.receivables = db.receivables.map((item) => updated.find((entry) => entry.id === item.id) || item);
  updated.forEach((entry) => {
    if (!existingIds.has(entry.id)) db.receivables.unshift(entry);
  });
  db.cash = [...(result?.cash || []), ...db.cash];
}

function customerCreditStats(customerId) {
  const items = db.receivables.filter((item) => item.customerId === customerId && item.method === "storeCredit" && item.status !== "cancelled");
  const openItems = items.filter((item) => receivableBalance(item) > 0);
  const overdueItems = openItems.filter((item) => item.dueDate < todayIso);
  return {
    totalCount: items.length,
    openCount: openItems.length,
    overdueCount: overdueItems.length,
    open: openItems.reduce((total, item) => total + receivableBalance(item), 0),
  };
}

async function savePayable(event) {
  event.preventDefault();
  const payable = {
    id: createId(),
    supplier: els.payableSupplier.value.trim(),
    category: els.payableCategory.value.trim(),
    amount: readNumber(els.payableAmount.value),
    issueDate: els.payableIssue.value,
    dueDate: els.payableDue.value,
    notes: els.payableNotes.value.trim(),
    paidAmount: 0,
    fee: 0,
    status: "pending",
    createdAt: new Date().toISOString(),
  };
  if (BACKEND_ENABLED) {
    try {
      const response = await fetch("/api/payables", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payable),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        alert(payload.error || "Não foi possível cadastrar a conta.");
        return;
      }
      applyPayableLocally(payload.data);
      persistLocalOnly();
      els.payableForm.reset();
      els.payableFormPanel.hidden = true;
      renderAll();
      return;
    } catch (error) {
      console.warn(error);
      alert("Não foi possível conectar ao servidor para cadastrar a conta.");
      return;
    }
  }
  db.payables.push(payable);
  persist();
  els.payableForm.reset();
  els.payableFormPanel.hidden = true;
  renderAll();
}

function renderPayables() {
  const openItems = db.payables.filter((item) => payableStatus(item) !== "paid");
  const overdueItems = db.payables.filter((item) => payableStatus(item) === "overdue");
  const todayItems = db.payables.filter((item) => payableStatus(item) === "today");
  const futureItems = db.payables.filter((item) => payableStatus(item) === "pending");
  els.payableTotalOpen.textContent = money.format(openItems.reduce((total, item) => total + item.amount, 0));
  els.payableTotalCount.textContent = `${openItems.length} conta${openItems.length === 1 ? "" : "s"}`;
  els.payableOverdueTotal.textContent = money.format(overdueItems.reduce((total, item) => total + item.amount, 0));
  els.payableOverdueCount.textContent = `${overdueItems.length} conta${overdueItems.length === 1 ? "" : "s"}`;
  els.payableTodayTotal.textContent = money.format(todayItems.reduce((total, item) => total + item.amount, 0));
  els.payableTodayCount.textContent = `${todayItems.length} conta${todayItems.length === 1 ? "" : "s"}`;
  els.payableFutureTotal.textContent = money.format(futureItems.reduce((total, item) => total + item.amount, 0));
  els.payableFutureCount.textContent = `${futureItems.length} conta${futureItems.length === 1 ? "" : "s"}`;
  const query = normalize(els.payableSearch.value);
  const category = els.payableCategoryFilter.value;
  const filter = els.payableFilter.value;
  const start = els.payableStart.value || "0000-01-01";
  const end = els.payableEnd.value || "9999-12-31";
  const items = db.payables.filter((item) => {
    const status = payableStatus(item);
    const text = [item.supplier, item.category, item.notes].join(" ");
    if (query && !normalize(text).includes(query)) return false;
    if (category !== "all" && item.category !== category) return false;
    if (item.dueDate < start || item.dueDate > end) return false;
    if (filter === "all") return true;
    if (filter === "open") return status === "pending" || status === "today" || status === "overdue";
    if (filter === "today") return status === "today";
    return status === filter;
  }).sort((a, b) => a.dueDate.localeCompare(b.dueDate));
  els.payableList.innerHTML = "";
  els.payableFooter.innerHTML = "";
  els.payableFoundCount.textContent = `${items.length} conta${items.length === 1 ? "" : "s"} encontrada${items.length === 1 ? "" : "s"}`;
  if (!items.length) {
    els.payableList.innerHTML = `<tr><td colspan="7" class="empty-cell">Nenhuma conta encontrada.</td></tr>`;
    els.payableFooter.textContent = "Mostrando 0 contas";
    return;
  }
  items.forEach((item) => {
    const status = payableStatus(item);
    const row = document.createElement("tr");
    const initials = (item.supplier || "CP").split(" ").filter(Boolean).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
    row.innerHTML = `
      <td><div class="payable-supplier-cell"><span>${escapeHtml(initials)}</span><div><strong>${escapeHtml(item.supplier || "-")}</strong><small>CNPJ: -</small></div></div></td>
      <td>${escapeHtml(item.category || "-")}</td>
      <td>${escapeHtml(item.notes || item.category || "-")}</td>
      <td>${formatDate(item.dueDate)}</td>
      <td>${money.format(item.amount + (item.fee || 0))}</td>
      <td>${payableStatusBadge(item)}</td>
      <td><div class="payable-actions"></div></td>
    `;
    const actions = row.querySelector(".payable-actions");
    actions.append(button("Ver", "ghost payable-icon-button", () => alert(`${item.supplier}\n${item.notes || item.category}\nVencimento: ${formatDate(item.dueDate)}\nValor: ${money.format(item.amount)}`)));
    actions.append(button("...", "stock-menu-button", () => payPayable(item.id), status === "paid"));
    els.payableList.append(row);
  });
  els.payableFooter.innerHTML = `
    <span>Mostrando 1 a ${items.length} de ${items.length} conta${items.length === 1 ? "" : "s"}</span>
    <div class="payable-pagination"><button type="button" disabled>Anterior</button><button type="button" class="active">1</button><button type="button" disabled>Próximo</button></div>
  `;
}

function payableStatusBadge(item) {
  const status = payableStatus(item);
  const labels = { paid: "Pago", overdue: "Vencida", today: "Vence hoje", pending: "A vencer" };
  const extra = status === "overdue" ? `<small>${diffDays(item.dueDate, todayIso)} dias de atraso</small>` : status === "pending" ? `<small>${diffDays(todayIso, item.dueDate)} dias</small>` : "";
  return `<span class="payable-status ${status}">${labels[status]}${extra}</span>`;
}

async function payPayable(id) {
  const item = db.payables.find((entry) => entry.id === id);
  if (!item) return;
  const fee = readNumber(prompt("Juros ou multa", "0"));
  const amount = item.amount + fee;
  if (BACKEND_ENABLED) {
    try {
      const response = await fetch(`/api/payables/${encodeURIComponent(id)}/pay`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fee, amount, method: "pix", paidAt: new Date().toISOString() }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        alert(payload.error || "Não foi possível baixar a conta.");
        return;
      }
      applyPayablePaymentResultLocally(payload.data);
      persistLocalOnly();
      renderAll();
      return;
    } catch (error) {
      console.warn(error);
      alert("Não foi possível conectar ao servidor para baixar a conta.");
      return;
    }
  }
  item.fee = fee;
  item.paidAmount = amount;
  item.status = "paid";
  item.paidAt = new Date().toISOString();
  addCash("out", "contas a pagar", item.category, "pix", amount, item.id);
  persist();
  renderAll();
}

async function saveCashMovement(event) {
  event.preventDefault();
  const movement = {
    direction: els.cashMovementType.value,
    type: "manual",
    description: els.cashMovementDescription.value.trim(),
    method: els.cashMovementMethod.value,
    amount: readNumber(els.cashMovementAmount.value),
    refId: "",
    createdAt: new Date().toISOString(),
  };
  if (BACKEND_ENABLED) {
    try {
      const response = await fetch("/api/cash-movements", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(movement),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        alert(payload.error || "Não foi possível registrar a movimentação.");
        return;
      }
      applyCashResultLocally(payload.data);
      persistLocalOnly();
      els.cashMovementForm.reset();
      els.cashMovementPanel.hidden = true;
      renderAll();
      return;
    } catch (error) {
      console.warn(error);
      alert("Não foi possível conectar ao servidor para registrar a movimentação.");
      return;
    }
  }
  addCash(movement.direction, movement.type, movement.description, movement.method, movement.amount, movement.refId, movement.createdAt);
  persist();
  els.cashMovementForm.reset();
  els.cashMovementPanel.hidden = true;
  renderAll();
}

async function saveBankAccountEntry(event) {
  event.preventDefault();
  const credit = readNumber(els.bankCreditAmount.value);
  const debit = readNumber(els.bankDebitAmount.value);
  const total = round(credit + debit);
  if (total <= 0) return alert("Informe um valor recebido no crédito ou no débito.");
  const createdAt = timestampForDateInput(els.bankAccountDate.value || todayIso);
  const description = els.bankAccountDescription.value.trim() || "Entrada em conta bancária";
  if (BACKEND_ENABLED) {
    try {
      const response = await fetch("/api/card-receipts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ credit, debit, description, createdAt, type: "conta bancária" }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        alert(payload.error || "Não foi possível registrar a entrada bancária.");
        return;
      }
      applyCashResultLocally(payload.data);
      persistLocalOnly();
      els.bankAccountForm.reset();
      els.bankAccountDate.value = todayIso;
      els.bankCreditAmount.value = "0";
      els.bankDebitAmount.value = "0";
      els.bankAccountPanel.hidden = true;
      renderAll();
      return;
    } catch (error) {
      console.warn(error);
      alert("Não foi possível conectar ao servidor para registrar a entrada bancária.");
      return;
    }
  }
  if (credit > 0) addCash("in", "conta bancária", `${description} - Crédito`, "card", credit, "", createdAt);
  if (debit > 0) addCash("in", "conta bancária", `${description} - Débito`, "card", debit, "", createdAt);
  settleCardPending(total, createdAt);
  persist();
  els.bankAccountForm.reset();
  els.bankAccountDate.value = todayIso;
  els.bankCreditAmount.value = "0";
  els.bankDebitAmount.value = "0";
  els.bankAccountPanel.hidden = true;
  renderAll();
}

function addCash(direction, type, description, method, amount, refId, createdAt = new Date().toISOString()) {
  if (amount <= 0) return;
  db.cash.push({ id: createId(), direction, type, description, method, amount, refId, createdAt });
}

function renderCash() {
  const total = db.cash.reduce((value, item) => value + (item.direction === "in" ? item.amount : -item.amount), 0);
  const todayItems = db.cash.filter((item) => item.createdAt.slice(0, 10) === todayIso);
  els.cashTotal.textContent = money.format(total);
  els.cashInToday.textContent = money.format(todayItems.filter((item) => item.direction === "in").reduce((value, item) => value + item.amount, 0));
  els.cashOutToday.textContent = money.format(todayItems.filter((item) => item.direction === "out").reduce((value, item) => value + item.amount, 0));
  renderCashClosingSummary();
  renderCashClosings();
  const start = els.cashStart.value || "0000-01-01";
  const end = els.cashEnd.value || "9999-12-31";
  const method = els.cashMethodFilter.value;
  const type = els.cashTypeFilter.value;
  let balance = 0;
  const rows = db.cash.slice().sort((a, b) => a.createdAt.localeCompare(b.createdAt)).map((item) => {
    balance += item.direction === "in" ? item.amount : -item.amount;
    return { ...item, balance };
  }).filter((item) => item.createdAt.slice(0, 10) >= start && item.createdAt.slice(0, 10) <= end && (method === "all" || item.method === method) && (type === "all" || item.direction === type));
  els.cashTimeline.innerHTML = "";
  els.cashFooter.innerHTML = "";
  els.cashTimeline.classList.toggle("empty", rows.length === 0);
  if (!rows.length) {
    els.cashTimeline.textContent = "Nenhuma movimentação.";
    return;
  }
  rows.reverse().forEach((item) => {
    const row = document.createElement("article");
    const isIn = item.direction === "in";
    const tag = isIn ? "Entrada" : "Saída";
    row.className = `cash-timeline-row ${isIn ? "in" : "out"}`;
    row.innerHTML = `
      <span class="cash-row-icon">${isIn ? "↓" : "↑"}</span>
      <div class="cash-row-main">
        <small>${formatDateTime(item.createdAt)} <em>${tag}</em></small>
        <strong>${escapeHtml(item.description || item.type)}</strong>
        <p>${escapeHtml(paymentLabels[item.method] || item.method || "-")}</p>
      </div>
      <div class="cash-row-value">
        <strong>${isIn ? "+" : "-"} ${money.format(item.amount)}</strong>
        <span>Saldo: ${money.format(item.balance)}</span>
      </div>
      <button type="button" class="stock-menu-button">...</button>
    `;
    els.cashTimeline.append(row);
  });
  els.cashFooter.innerHTML = `
    <span>Mostrando ${rows.length} de ${rows.length} movimentaç${rows.length === 1 ? "ão" : "ões"}</span>
    <div class="cash-pagination"><button type="button" disabled>Anterior</button><button type="button" class="active">1</button><button type="button" disabled>Próximo</button></div>
  `;
}

function cashClosingMetrics(date = todayIso) {
  const target = String(date || todayIso).slice(0, 10);
  const until = db.cash.filter((item) => String(item.createdAt || "").slice(0, 10) <= target);
  const day = db.cash.filter((item) => String(item.createdAt || "").slice(0, 10) === target);
  const signed = (items, method = null) => round(items
    .filter((item) => !method || item.method === method)
    .reduce((value, item) => value + (item.direction === "in" ? Number(item.amount || 0) : -Number(item.amount || 0)), 0));
  return {
    expectedCash: signed(until, "cash"),
    totalBalance: signed(until),
    cashIn: round(day.filter((item) => item.direction === "in" && item.method === "cash").reduce((value, item) => value + Number(item.amount || 0), 0)),
    cashOut: round(day.filter((item) => item.direction === "out" && item.method === "cash").reduce((value, item) => value + Number(item.amount || 0), 0)),
  };
}

function renderCashClosingSummary() {
  if (!els.cashClosingExpected) return;
  const metrics = cashClosingMetrics(els.cashClosingDate.value || todayIso);
  const informed = readNumber(els.cashClosingInformed.value);
  const difference = round(informed - metrics.expectedCash);
  els.cashClosingExpected.textContent = money.format(metrics.expectedCash);
  els.cashClosingDifference.textContent = money.format(difference);
  els.cashClosingDifference.classList.toggle("value-bad", Math.abs(difference) > 0.01);
  els.cashClosingTotalBalance.textContent = money.format(metrics.totalBalance);
}

async function saveCashClosing(event) {
  event.preventDefault();
  const date = els.cashClosingDate.value || todayIso;
  const informedCash = readNumber(els.cashClosingInformed.value);
  const notes = els.cashClosingNotes.value.trim();
  if (BACKEND_ENABLED) {
    try {
      const response = await fetch("/api/cash-closings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date, informedCash, notes }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        alert(payload.error || "Não foi possível registrar o fechamento.");
        return;
      }
      db.cashClosings = [payload.data, ...db.cashClosings.filter((item) => item.id !== payload.data.id)];
      persistLocalOnly();
      els.cashClosingForm.reset();
      els.cashClosingDate.value = todayIso;
      renderAll();
      return;
    } catch (error) {
      console.warn(error);
      alert("Não foi possível conectar ao servidor para registrar o fechamento.");
      return;
    }
  }
  const metrics = cashClosingMetrics(date);
  const closing = {
    id: createId(),
    date,
    expectedCash: metrics.expectedCash,
    informedCash,
    difference: round(informedCash - metrics.expectedCash),
    totalBalance: metrics.totalBalance,
    cashIn: metrics.cashIn,
    cashOut: metrics.cashOut,
    notes,
    userId: session?.id || "",
    userName: session?.name || "Operador",
    createdAt: new Date().toISOString(),
  };
  db.cashClosings.unshift(closing);
  persist();
  els.cashClosingForm.reset();
  els.cashClosingDate.value = todayIso;
  renderAll();
}

function renderCashClosings() {
  if (!els.cashClosingList) return;
  const closings = (db.cashClosings || []).slice().sort((a, b) => String(b.createdAt || "").localeCompare(String(a.createdAt || ""))).slice(0, 8);
  els.cashClosingList.classList.toggle("empty", closings.length === 0);
  els.cashClosingList.innerHTML = closings.length
    ? closings.map((closing) => `
      <article class="cash-closing-row">
        <div>
          <strong>${formatDate(closing.date)}</strong>
          <small>${escapeHtml(closing.userName || "Operador")} | ${formatDateTime(closing.createdAt)}</small>
          ${closing.notes ? `<small>${escapeHtml(closing.notes)}</small>` : ""}
        </div>
        <div><span>Esperado</span><strong>${money.format(closing.expectedCash || 0)}</strong></div>
        <div><span>Informado</span><strong>${money.format(closing.informedCash || 0)}</strong></div>
        <div><span>Diferença</span><strong class="${Math.abs(Number(closing.difference || 0)) > 0.01 ? "value-bad" : ""}">${money.format(closing.difference || 0)}</strong></div>
      </article>
    `).join("")
    : "Nenhum fechamento registrado.";
}

async function receiveCards(event) {
  event.preventDefault();
  const amount = readNumber(els.cardReceiptAmount.value);
  const description = els.cardReceiptDescription.value.trim();
  if (BACKEND_ENABLED) {
    try {
      const response = await fetch("/api/card-receipts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ amount, description, type: "receber cartoes", createdAt: new Date().toISOString() }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        alert(payload.error || "Não foi possível lançar o recebimento no caixa.");
        return;
      }
      applyCashResultLocally(payload.data);
      persistLocalOnly();
      els.cardReceiptForm.reset();
      renderAll();
      return;
    } catch (error) {
      console.warn(error);
      alert("Não foi possível conectar ao servidor para lançar o recebimento.");
      return;
    }
  }
  addCash("in", "receber cartoes", description, "card", amount, "");
  settleCardPending(amount);
  persist();
  els.cardReceiptForm.reset();
  renderAll();
}

function renderCards() {
  const pending = db.receivables.filter((item) => item.status === "cardPending");
  els.cardPendingList.innerHTML = "";
  els.cardPendingList.classList.toggle("empty", pending.length === 0);
  if (!pending.length) {
    els.cardPendingList.textContent = "Nenhum cartao pendente.";
    return;
  }
  pending.forEach((item) => els.cardPendingList.append(tableRow(`${paymentLabels[item.method]} | Venda ${item.saleId || "-"}`, item.customerName || "Venda simples", money.format(item.amount - item.received))));
}

function renderDashboard() {
  const dashboardRange = Math.max(1, Math.floor(readNumber(els.dashSalesRange.value || "30")));
  const dashboardKey = `${todayIso}:${dashboardRange}`;
  if (BACKEND_ENABLED) {
    requestDashboardSummary(dashboardRange, dashboardKey);
    if (dashboardApiCache && dashboardApiKey === dashboardKey) {
      renderDashboardFromSummary(dashboardApiCache);
      return;
    }
  }
  const month = todayIso.slice(0, 7);
  const validSales = db.sales.filter((sale) => sale.status !== "cancelled");
  const todaySales = validSales.filter((sale) => sale.createdAt.slice(0, 10) === todayIso);
  const monthSales = validSales.filter((sale) => sale.createdAt.slice(0, 7) === month);
  const todayCash = db.cash.filter((item) => item.createdAt.slice(0, 10) === todayIso);
  const cashBalance = db.cash.reduce((value, item) => value + (item.direction === "in" ? item.amount : -item.amount), 0);
  const cashInToday = todayCash.filter((item) => item.direction === "in").reduce((value, item) => value + item.amount, 0);
  const cashOutToday = todayCash.filter((item) => item.direction === "out").reduce((value, item) => value + item.amount, 0);
  const openPayables = db.payables.filter((item) => payableStatus(item) !== "paid");
  const openReceivables = db.receivables.filter((item) => item.method === "storeCredit" && item.status !== "cancelled" && receivableBalance(item) > 0);
  const stockValue = db.products.reduce((total, product) => total + product.stock * product.cost, 0);
  els.dashTodaySales.textContent = money.format(sum(todaySales, "total"));
  els.dashMonthSales.textContent = money.format(sum(monthSales, "total"));
  els.dashMonthProfit.textContent = money.format(monthSales.reduce((total, sale) => total + sale.total - sale.costTotal, 0));
  els.dashStockValue.textContent = money.format(stockValue);
  els.dashCreditOpen.textContent = money.format(openReceivables.reduce((total, item) => total + receivableBalance(item), 0));
  els.dashCashBalance.textContent = money.format(cashBalance);
  els.dashCashIn.textContent = money.format(cashInToday);
  els.dashCashOut.textContent = money.format(cashOutToday);
  els.dashPayablesOpen.textContent = money.format(openPayables.reduce((total, item) => total + item.amount, 0));
  els.dashPayablesCount.textContent = `${openPayables.length} conta${openPayables.length === 1 ? "" : "s"} em aberto`;
  els.dashReceivableOpen.textContent = money.format(openReceivables.reduce((total, item) => total + receivableBalance(item), 0));
  els.dashReceivableCount.textContent = `${openReceivables.length} parcela${openReceivables.length === 1 ? "" : "s"} em aberto`;
  els.topDateLabel.textContent = new Intl.DateTimeFormat("pt-BR", { dateStyle: "full" }).format(new Date(`${todayIso}T00:00:00`));
  renderSalesChart();
  renderDashboardPanels(validSales);
}

async function requestDashboardSummary(range, key) {
  if (dashboardApiLoading || dashboardApiKey === key) return;
  dashboardApiLoading = true;
  try {
    const response = await fetch(`/api/dashboard?range=${encodeURIComponent(range)}&date=${encodeURIComponent(todayIso)}`, { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (response.ok && payload.data) {
      dashboardApiCache = payload.data;
      dashboardApiKey = key;
      renderDashboardFromSummary(payload.data);
    }
  } catch (error) {
    console.warn(error);
  } finally {
    dashboardApiLoading = false;
  }
}

function renderDashboardFromSummary(summary) {
  const metrics = summary.metrics || {};
  els.dashTodaySales.textContent = money.format(metrics.todaySales || 0);
  els.dashMonthSales.textContent = money.format(metrics.monthSales || 0);
  els.dashMonthProfit.textContent = money.format(metrics.monthProfit || 0);
  els.dashStockValue.textContent = money.format(metrics.stockValue || 0);
  els.dashCreditOpen.textContent = money.format(metrics.creditOpen || 0);
  els.dashCashBalance.textContent = money.format(metrics.cashBalance || 0);
  els.dashCashIn.textContent = money.format(metrics.cashInToday || 0);
  els.dashCashOut.textContent = money.format(metrics.cashOutToday || 0);
  els.dashPayablesOpen.textContent = money.format(metrics.payablesOpen || 0);
  els.dashPayablesCount.textContent = `${metrics.payablesCount || 0} conta${metrics.payablesCount === 1 ? "" : "s"} em aberto`;
  els.dashReceivableOpen.textContent = money.format(metrics.receivableOpen || 0);
  els.dashReceivableCount.textContent = `${metrics.receivableCount || 0} parcela${metrics.receivableCount === 1 ? "" : "s"} em aberto`;
  els.topDateLabel.textContent = new Intl.DateTimeFormat("pt-BR", { dateStyle: "full" }).format(new Date(`${summary.today || todayIso}T00:00:00`));
  renderSalesChartFromSummary(summary.salesChart || []);
  renderPaymentSummaryFromSummary(summary.payments || {});
  renderTopBrandsFromSummary(summary.topBrands || []);
  renderStoppedProductsFromSummary(summary.stoppedProducts || []);
}

function renderDashboardPanels(validSales) {
  renderPaymentSummary(validSales);
  renderTopBrands(validSales);
  renderStoppedProducts(validSales);
  renderFinanceSummary();
}

function renderPaymentSummary(validSales) {
  const payments = validSales.flatMap((sale) => sale.payments);
  const total = payments.reduce((value, payment) => value + payment.amount, 0);
  const colors = { cash: "#58bd4d", pix: "#2dbdc9", debit: "#ff841a", credit: "#9d54db", storeCredit: "#f45d8b" };
  const rows = ["cash", "pix", "debit", "credit", "storeCredit"].map((method) => {
    const amount = payments.filter((payment) => payment.method === method).reduce((value, payment) => value + payment.amount, 0);
    const percent = total ? Math.round((amount / total) * 100) : 0;
    const salesCount = validSales.filter((sale) => sale.payments.some((payment) => payment.method === method && payment.amount > 0)).length;
    return { method, amount, percent, salesCount, color: colors[method] };
  });
  const activeRows = rows.filter((item) => item.amount > 0);
  let start = 0;
  const segments = activeRows.map((item) => {
    const end = start + (item.amount / total) * 100;
    const segment = `${item.color} ${start}% ${end}%`;
    start = end;
    return segment;
  }).join(", ") || "#eef2f6 0% 100%";
  const totalSales = validSales.length;
  const paymentTooltip = rows.map((item) => `${paymentLabels[item.method]}: ${item.percent}% | ${money.format(item.amount)} | ${item.salesCount} venda${item.salesCount === 1 ? "" : "s"}`).join("\n");
  els.paymentSummary.innerHTML = `
    <div class="payment-clean-head">
      <span class="payment-clean-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 3v9l7 4"></path><path d="M21 12a9 9 0 1 1-9-9"></path><path d="M12 3a9 9 0 0 1 9 9h-9V3Z"></path></svg></span>
      <div><h2>Vendas por forma de pagamento</h2><p>Veja a distribuição das vendas por forma de pagamento.</p></div>
      <button type="button" class="payment-menu-button" aria-label="Opções">⋮</button>
    </div>
    <div class="payment-clean-body">
      <div class="payment-donut" data-tooltip="${escapeHtml(`Total: ${money.format(total)}\n${paymentTooltip}`)}" style="background: conic-gradient(${segments})"><span>Total<strong>${money.format(total)}</strong></span></div>
      <div class="payment-clean-legend">${rows.map((item) => `
        <article style="--payment-color:${item.color}" data-tooltip="${escapeHtml(`${paymentLabels[item.method]}\n${item.percent}% do total\n${money.format(item.amount)}\n${item.salesCount} venda${item.salesCount === 1 ? "" : "s"}`)}">
          <i></i>
          <div><strong>${paymentLabels[item.method]}</strong><span>${item.salesCount} venda${item.salesCount === 1 ? "" : "s"}</span></div>
          <div><b>${item.percent}%</b><span>${money.format(item.amount)}</span></div>
        </article>
      `).join("")}</div>
    </div>
    <div class="payment-total-strip">
      <span class="payment-total-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 20V10"></path><path d="M12 20V4"></path><path d="M19 20v-7"></path></svg></span>
      <div><strong>Total de vendas</strong><span>${totalSales} venda${totalSales === 1 ? "" : "s"} realizada${totalSales === 1 ? "" : "s"}</span></div>
      <div><strong>${money.format(total)}</strong><span>100% do total</span></div>
    </div>
  `;
  bindChartTooltips(els.paymentSummary);
}

function renderPaymentSummaryFromSummary(summary) {
  const colors = { cash: "#58bd4d", pix: "#2dbdc9", debit: "#ff841a", credit: "#9d54db", storeCredit: "#f45d8b" };
  const total = summary.total || 0;
  const rows = ["cash", "pix", "debit", "credit", "storeCredit"].map((method) => {
    const item = (summary.rows || []).find((row) => row.method === method) || {};
    return { method, amount: item.amount || 0, percent: item.percent || 0, salesCount: item.salesCount || 0, color: colors[method] };
  });
  const activeRows = rows.filter((item) => item.amount > 0);
  let start = 0;
  const segments = activeRows.map((item) => {
    const end = start + (item.amount / total) * 100;
    const segment = `${item.color} ${start}% ${end}%`;
    start = end;
    return segment;
  }).join(", ") || "#eef2f6 0% 100%";
  const totalSales = summary.totalSales || 0;
  const paymentTooltip = rows.map((item) => `${paymentLabels[item.method]}: ${item.percent}% | ${money.format(item.amount)} | ${item.salesCount} venda${item.salesCount === 1 ? "" : "s"}`).join("\n");
  els.paymentSummary.innerHTML = `
    <div class="payment-clean-head">
      <span class="payment-clean-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 3v9l7 4"></path><path d="M21 12a9 9 0 1 1-9-9"></path><path d="M12 3a9 9 0 0 1 9 9h-9V3Z"></path></svg></span>
      <div><h2>Vendas por forma de pagamento</h2><p>Veja a distribuição das vendas por forma de pagamento.</p></div>
      <button type="button" class="payment-menu-button" aria-label="Opções">⋮</button>
    </div>
    <div class="payment-clean-body">
      <div class="payment-donut" data-tooltip="${escapeHtml(`Total: ${money.format(total)}\n${paymentTooltip}`)}" style="background: conic-gradient(${segments})"><span>Total<strong>${money.format(total)}</strong></span></div>
      <div class="payment-clean-legend">${rows.map((item) => `
        <article style="--payment-color:${item.color}" data-tooltip="${escapeHtml(`${paymentLabels[item.method]}\n${item.percent}% do total\n${money.format(item.amount)}\n${item.salesCount} venda${item.salesCount === 1 ? "" : "s"}`)}">
          <i></i>
          <div><strong>${paymentLabels[item.method]}</strong><span>${item.salesCount} venda${item.salesCount === 1 ? "" : "s"}</span></div>
          <div><b>${item.percent}%</b><span>${money.format(item.amount)}</span></div>
        </article>
      `).join("")}</div>
    </div>
    <div class="payment-total-strip">
      <span class="payment-total-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 20V10"></path><path d="M12 20V4"></path><path d="M19 20v-7"></path></svg></span>
      <div><strong>Total de vendas</strong><span>${totalSales} venda${totalSales === 1 ? "" : "s"} realizada${totalSales === 1 ? "" : "s"}</span></div>
      <div><strong>${money.format(total)}</strong><span>100% do total</span></div>
    </div>
  `;
  bindChartTooltips(els.paymentSummary);
}

function renderTopBrands(validSales) {
  const map = new Map();
  validSales.forEach((sale) => sale.items.forEach((item) => {
    const product = db.products.find((entry) => entry.id === item.productId);
    const brand = item.brand || product?.brand || "Sem marca";
    const current = map.get(brand) || { name: brand, qty: 0 };
    current.qty += item.quantity;
    map.set(brand, current);
  }));
  const rows = [...map.values()].sort((a, b) => b.qty - a.qty).slice(0, 5);
  els.topProductsList.innerHTML = rows.length
    ? rows.map((item) => `<div class="summary-row"><span>${escapeHtml(item.name)}</span><strong>${item.qty}</strong></div>`).join("")
    : `<p class="empty">Sem vendas registradas.</p>`;
}

function renderTopBrandsFromSummary(rows) {
  els.topProductsList.innerHTML = rows.length
    ? rows.map((item) => `<div class="summary-row"><span>${escapeHtml(item.name)}</span><strong>${item.qty}</strong></div>`).join("")
    : `<p class="empty">Sem vendas registradas.</p>`;
}

function renderStoppedProducts(validSales) {
  const lastSaleByProduct = new Map();
  validSales.forEach((sale) => sale.items.forEach((item) => {
    const current = lastSaleByProduct.get(item.productId) || "";
    if (!current || sale.createdAt > current) lastSaleByProduct.set(item.productId, sale.createdAt);
  }));
  const rows = db.products.map((product) => {
    const baseDate = lastSaleByProduct.get(product.id) || product.updatedAt || todayIso;
    return { product, days: diffDays(todayIso, String(baseDate).slice(0, 10)) };
  }).filter((item) => item.days > 90 && item.product.stock > 0).sort((a, b) => b.days - a.days).slice(0, 6);
  els.lowStockList.innerHTML = rows.length
    ? rows.map(({ product, days }) => `<div class="summary-row danger-text"><span>${escapeHtml(product.name)}</span><strong>${days} dias</strong><small>Estoque ${product.stock}</small></div>`).join("")
    : `<p class="empty">Sem peças paradas acima de 90 dias.</p>`;
}

function renderStoppedProductsFromSummary(rows) {
  els.lowStockList.innerHTML = rows.length
    ? rows.map((item) => `<div class="summary-row danger-text"><span>${escapeHtml(item.name)}</span><strong>${item.days} dias</strong><small>Estoque ${item.stock}</small></div>`).join("")
    : `<p class="empty">Sem peças paradas acima de 90 dias.</p>`;
}

function renderFinanceSummary() {
  const openReceivables = db.receivables.filter((item) => item.method === "storeCredit").reduce((total, item) => total + receivableBalance(item), 0);
  const openPayables = db.payables.filter((item) => payableStatus(item) !== "paid").reduce((total, item) => total + item.amount, 0);
  const cards = db.receivables.filter((item) => item.status === "cardPending").reduce((total, item) => total + item.amount - item.received, 0);
  const overdue = db.receivables.filter((item) => item.method === "storeCredit" && item.dueDate < todayIso).reduce((total, item) => total + receivableBalance(item), 0);
  els.financeSummaryList.innerHTML = [
    ["Contas a receber", openReceivables, "good-text"],
    ["Contas a pagar", openPayables, "danger-text"],
    ["Cartões a receber", cards, "info-text"],
    ["Crediário vencido", overdue, "danger-text"],
  ].map(([label, value, className]) => `<div class="summary-row"><span>${label}</span><strong class="${className}">${money.format(value)}</strong></div>`).join("");
}

function renderSalesChart() {
  const days = Math.max(1, Math.floor(readNumber(els.dashSalesRange.value || "30")));
  const startDate = new Date(`${todayIso}T00:00:00`);
  startDate.setDate(startDate.getDate() - days + 1);
  const dates = datesBetween(toDateInput(startDate), todayIso);
  const values = dates.map((date) => ({ date, total: sum(db.sales.filter((sale) => sale.status !== "cancelled" && sale.createdAt.slice(0, 10) === date), "total") }));
  const max = Math.max(...values.map((item) => item.total), 0);
  const width = 680;
  const height = 220;
  const pad = 22;
  const points = values.map((item, index) => {
    const x = values.length === 1 ? width / 2 : pad + (index / (values.length - 1)) * (width - pad * 2);
    const y = max ? height - pad - (item.total / max) * (height - pad * 2) : height - pad;
    return { ...item, x, y };
  });
  const path = points.map((point, index) => `${index ? "L" : "M"}${point.x.toFixed(1)} ${point.y.toFixed(1)}`).join(" ");
  els.salesChart.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Evolução de vendas por dia">
      <path class="line-area" d="${path} L${width - pad} ${height - pad} L${pad} ${height - pad} Z"></path>
      <path class="line-path" d="${path}"></path>
      ${points.map((point) => {
        const daySales = db.sales.filter((sale) => sale.status !== "cancelled" && sale.createdAt.slice(0, 10) === point.date);
        const pieces = daySales.flatMap((sale) => sale.items || []).reduce((totalPieces, item) => totalPieces + Number(item.quantity || 0), 0);
        const tooltip = `Vendas por dia\n${formatDate(point.date)}\nTotal: ${money.format(point.total)}\nVendas: ${daySales.length}\nPeças: ${pieces}`;
        return `<circle class="line-point" cx="${point.x.toFixed(1)}" cy="${point.y.toFixed(1)}" r="3"></circle><circle class="line-hit-area" cx="${point.x.toFixed(1)}" cy="${point.y.toFixed(1)}" r="11" data-tooltip="${escapeHtml(tooltip)}"></circle>`;
      }).join("")}
      <text x="${pad}" y="${height - 4}">${formatDate(values[0]?.date || todayIso)}</text>
      <text x="${width - pad}" y="${height - 4}" text-anchor="end">${formatDate(values.at(-1)?.date || todayIso)}</text>
    </svg>
  `;
  bindChartTooltips(els.salesChart);
}

function renderSalesChartFromSummary(values) {
  const rows = values.length ? values : [{ date: todayIso, total: 0, salesCount: 0, pieces: 0 }];
  const max = Math.max(...rows.map((item) => item.total), 0);
  const width = 680;
  const height = 220;
  const pad = 22;
  const points = rows.map((item, index) => {
    const x = rows.length === 1 ? width / 2 : pad + (index / (rows.length - 1)) * (width - pad * 2);
    const y = max ? height - pad - (item.total / max) * (height - pad * 2) : height - pad;
    return { ...item, x, y };
  });
  const path = points.map((point, index) => `${index ? "L" : "M"}${point.x.toFixed(1)} ${point.y.toFixed(1)}`).join(" ");
  els.salesChart.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Evolução de vendas por dia">
      <path class="line-area" d="${path} L${width - pad} ${height - pad} L${pad} ${height - pad} Z"></path>
      <path class="line-path" d="${path}"></path>
      ${points.map((point) => {
        const tooltip = `Vendas por dia\n${formatDate(point.date)}\nTotal: ${money.format(point.total)}\nVendas: ${point.salesCount || 0}\nPeças: ${point.pieces || 0}`;
        return `<circle class="line-point" cx="${point.x.toFixed(1)}" cy="${point.y.toFixed(1)}" r="3"></circle><circle class="line-hit-area" cx="${point.x.toFixed(1)}" cy="${point.y.toFixed(1)}" r="11" data-tooltip="${escapeHtml(tooltip)}"></circle>`;
      }).join("")}
      <text x="${pad}" y="${height - 4}">${formatDate(rows[0]?.date || todayIso)}</text>
      <text x="${width - pad}" y="${height - 4}" text-anchor="end">${formatDate(rows.at(-1)?.date || todayIso)}</text>
    </svg>
  `;
  bindChartTooltips(els.salesChart);
}

function renderReports() {
  const start = els.reportStart.value || todayIso;
  const end = els.reportEnd.value || start;
  const reportKey = `${start}:${end}:${todayIso}`;
  if (BACKEND_ENABLED) {
    requestReportsSummary(start, end, reportKey);
    if (reportsApiCache && reportsApiKey === reportKey) {
      renderReportsFromSummary(reportsApiCache);
      return;
    }
  }
  const sales = db.sales.filter((sale) => sale.createdAt.slice(0, 10) >= start && sale.createdAt.slice(0, 10) <= end);
  const validSales = sales.filter((sale) => sale.status !== "cancelled");
  const pieces = validSales.flatMap((sale) => sale.items);
  const topCustomers = db.customers.map((customer) => ({ name: customer.name, total: sum(validSales.filter((sale) => sale.customerId === customer.id), "total") })).filter((item) => item.total > 0).sort((a, b) => b.total - a.total);
  const stopped = db.products.filter((product) => !pieces.some((item) => item.productId === product.id));
  const reports = [
    ["Venda", [`Total: ${money.format(sum(validSales, "total"))}`, `Ticket médio: ${money.format(validSales.length ? sum(validSales, "total") / validSales.length : 0)}`, `Produtos vendidos: ${pieces.reduce((total, item) => total + item.quantity, 0)}`, `Canceladas: ${sales.filter((sale) => sale.status === "cancelled").length}`]],
    ["Clientes", [`Cadastrados: ${db.customers.length}`, `Mais compram: ${topCustomers.slice(0, 3).map((item) => `${item.name} ${money.format(item.total)}`).join(", ") || "-"}`, `Inadimplentes: ${new Set(db.receivables.filter((item) => item.method === "storeCredit" && item.dueDate < todayIso && receivableBalance(item) > 0).map((item) => item.customerId)).size}`]],
    ["Contas a pagar", [`Pendentes: ${money.format(db.payables.filter((item) => payableStatus(item) !== "paid").reduce((total, item) => total + item.amount, 0))}`]],
    ["Contas a receber", [`Crediário: ${money.format(db.receivables.filter((item) => item.method === "storeCredit").reduce((total, item) => total + receivableBalance(item), 0))}`]],
    ["Recebimentos", Object.keys(paymentLabels).map((method) => `${paymentLabels[method]}: ${money.format(validSales.flatMap((sale) => sale.payments).filter((payment) => payment.method === method).reduce((total, payment) => total + payment.amount, 0))}`)],
    ["Produtos parados", stopped.slice(0, 8).map((product) => product.name)],
  ];
  els.reportsList.innerHTML = reports.map(([title, lines]) => `<article class="report-card"><h3>${title}</h3><ul>${lines.map((line) => `<li>${escapeHtml(line)}</li>`).join("")}</ul></article>`).join("");
}

async function requestReportsSummary(start, end, key) {
  if (reportsApiLoading || reportsApiKey === key) return;
  reportsApiLoading = true;
  try {
    const params = new URLSearchParams({ start, end, today: todayIso });
    const response = await fetch(`/api/reports?${params.toString()}`, { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (response.ok && payload.data) {
      reportsApiCache = payload.data;
      reportsApiKey = key;
      renderReportsFromSummary(payload.data);
    }
  } catch (error) {
    console.warn(error);
  } finally {
    reportsApiLoading = false;
  }
}

function renderReportsFromSummary(summary) {
  const reports = summary.reports || [];
  els.reportsList.innerHTML = reports.map((report) => `
    <article class="report-card">
      <h3>${escapeHtml(report.title)}</h3>
      <ul>${(report.lines || []).map((line) => `<li>${escapeHtml(line)}</li>`).join("") || "<li>-</li>"}</ul>
    </article>
  `).join("");
}

async function loadDatabaseStatus(force = false) {
  if (!BACKEND_ENABLED || !isAdmin()) return;
  if (databaseStatusLoading || (databaseStatusLoaded && !force)) {
    renderDatabaseStatus();
    return;
  }
  databaseStatusLoading = true;
  els.databaseStatusText.textContent = "Verificando banco...";
  try {
    const response = await fetch("/api/database/status", { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      els.databaseStatusText.textContent = payload.error || "Não foi possível verificar o banco.";
      return;
    }
    databaseStatus = payload.data || null;
    databaseStatusLoaded = true;
    renderDatabaseStatus();
  } catch (error) {
    console.warn(error);
    els.databaseStatusText.textContent = "Não foi possível conectar ao servidor.";
  } finally {
    databaseStatusLoading = false;
  }
}

function renderDatabaseStatus() {
  if (!els.databaseStatusList) return;
  if (!databaseStatus) {
    els.databaseStatusList.classList.add("empty");
    els.databaseStatusList.textContent = "Nenhuma informação carregada.";
    return;
  }
  const ok = databaseStatus.integrity === "ok" && Number(databaseStatus.foreignKeyErrors || 0) === 0;
  els.databaseStatusText.textContent = ok ? "Banco íntegro." : "Banco exige atenção.";
  els.databaseStatusList.classList.remove("empty");
  const counts = databaseStatus.counts || {};
  const countSummary = [
    ["Produtos", counts.products],
    ["Clientes", counts.customers],
    ["Vendas", counts.sales],
    ["Caixa", counts.cash_movements],
    ["Recebíveis", counts.receivables],
    ["Contas", counts.payables],
  ].map(([label, value]) => `${label}: ${Number(value || 0)}`).join(" | ");
  els.databaseStatusList.innerHTML = [
    databaseStatusCard("Integridade", ok ? "OK" : "Atenção", `${databaseStatus.foreignKeyErrors || 0} erro${Number(databaseStatus.foreignKeyErrors || 0) === 1 ? "" : "s"} de vínculo`, ok ? "good" : "bad"),
    databaseStatusCard("Arquivo", formatBytes(databaseStatus.size || 0), escapeHtml(databaseStatus.filename || "-")),
    databaseStatusCard("Modo", String(databaseStatus.journalMode || "-").toUpperCase(), `Timeout ${databaseStatus.busyTimeoutMs || 0} ms`),
    databaseStatusCard("WAL", formatBytes(databaseStatus.walSize || 0), "Diário de escrita"),
    databaseStatusCard("Backups", String(databaseStatus.backupCount || 0), databaseStatus.lastBackup ? formatDateTime(databaseStatus.lastBackup.createdAt) : "Nenhum backup"),
    databaseStatusCard("Registros", countSummary, "Tabelas principais"),
  ].join("");
}

function databaseStatusCard(title, value, detail, status = "") {
  return `
    <article class="database-status-card ${status}">
      <span>${escapeHtml(title)}</span>
      <strong>${escapeHtml(value)}</strong>
      <small>${escapeHtml(detail)}</small>
    </article>
  `;
}

async function loadBackups(force = false) {
  if (!BACKEND_ENABLED || !isAdmin()) return;
  if (backupsLoading || (backupsLoaded && !force)) {
    renderBackups();
    return;
  }
  backupsLoading = true;
  els.backupStatus.textContent = "Carregando backups...";
  try {
    const response = await fetch("/api/backups", { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      els.backupStatus.textContent = payload.error || "Não foi possível carregar os backups.";
      return;
    }
    backups = payload.data || [];
    backupsLoaded = true;
    renderBackups();
  } catch (error) {
    console.warn(error);
    els.backupStatus.textContent = "Não foi possível conectar ao servidor.";
  } finally {
    backupsLoading = false;
  }
}

async function createBackup() {
  if (!BACKEND_ENABLED || !isAdmin()) return;
  els.createBackupButton.disabled = true;
  els.backupStatus.textContent = "Criando backup...";
  try {
    const response = await fetch("/api/backups", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reason: "manual" }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      alert(payload.error || "Não foi possível criar o backup.");
      return;
    }
    backups = [payload.data, ...backups.filter((item) => item.filename !== payload.data.filename)];
    backupsLoaded = true;
    renderBackups();
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para criar o backup.");
  } finally {
    els.createBackupButton.disabled = false;
  }
}

async function exportSystemData() {
  if (!BACKEND_ENABLED) {
    const blob = new Blob([JSON.stringify({ system: "Mova Sports", exportedAt: new Date().toISOString(), data: db }, null, 2)], { type: "application/json;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `mova-sports-export-${todayIso}.json`;
    link.click();
    URL.revokeObjectURL(url);
    return;
  }
  try {
    const response = await fetch("/api/export", { cache: "no-store" });
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      alert(payload.error || "Não foi possível exportar os dados.");
      return;
    }
    const blob = await response.blob();
    const disposition = response.headers.get("Content-Disposition") || "";
    const match = disposition.match(/filename="([^"]+)"/);
    const filename = match ? match[1] : `mova-sports-export-${todayIso}.json`;
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  } catch {
    alert("Não foi possível conectar ao servidor para exportar os dados.");
  }
}

function renderBackups() {
  if (!els.backupList) return;
  els.backupList.classList.toggle("empty", backups.length === 0);
  els.backupStatus.textContent = backups.length ? `${backups.length} backup${backups.length === 1 ? "" : "s"} encontrado${backups.length === 1 ? "" : "s"}.` : "Nenhum backup encontrado.";
  els.backupList.innerHTML = backups.length
    ? backups.map((backup) => `
      <article class="backup-row">
        <span class="backup-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 20h14V8l-4-4H5v16Z"></path><path d="M15 4v5h4"></path><path d="M8 13h8"></path><path d="M8 17h5"></path></svg></span>
        <div>
          <strong>${escapeHtml(backup.filename)}</strong>
          <small>${formatDateTime(backup.createdAt)} • ${formatBytes(backup.size || 0)}</small>
        </div>
      </article>
    `).join("")
    : "Nenhum backup encontrado.";
}

async function loadAuditLogs(force = false) {
  if (!BACKEND_ENABLED || !isAdmin()) return;
  if (auditLogsLoading || (auditLogsLoaded && !force)) {
    renderAuditLogs();
    return;
  }
  auditLogsLoading = true;
  els.auditStatus.textContent = "Carregando auditoria...";
  const params = new URLSearchParams({ limit: els.auditLimit.value || "100" });
  if (els.auditModuleFilter.value) params.set("module", els.auditModuleFilter.value);
  if (els.auditActionFilter.value) params.set("action", els.auditActionFilter.value);
  try {
    const response = await fetch(`/api/audit-logs?${params.toString()}`, { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      els.auditStatus.textContent = payload.error || "Não foi possível carregar a auditoria.";
      return;
    }
    auditLogs = payload.data || [];
    auditLogsLoaded = true;
    renderAuditLogs();
  } catch (error) {
    console.warn(error);
    els.auditStatus.textContent = "Não foi possível conectar ao servidor.";
  } finally {
    auditLogsLoading = false;
  }
}

function renderAuditLogs() {
  if (!els.auditList) return;
  const query = normalize(els.auditSearch.value || "");
  const filtered = auditLogs.filter((item) => {
    if (!query) return true;
    const text = [
      item.userName,
      item.userRole,
      item.action,
      item.module,
      item.refId,
      auditLogSummary(item),
      JSON.stringify(item.details || {}),
    ].join(" ");
    return normalize(text).includes(query);
  });
  els.auditList.classList.toggle("empty", filtered.length === 0);
  els.auditStatus.textContent = filtered.length ? `${filtered.length} registro${filtered.length === 1 ? "" : "s"} encontrado${filtered.length === 1 ? "" : "s"}.` : "Nenhum registro encontrado.";
  els.auditList.innerHTML = filtered.length
    ? filtered.map((item) => `
      <article class="audit-row">
        <span class="audit-icon ${escapeHtml(item.action || "")}" aria-hidden="true">${auditActionIcon(item.action)}</span>
        <div class="audit-main">
          <strong>${escapeHtml(auditModuleLabel(item.module))} • ${escapeHtml(auditActionLabel(item.action))}</strong>
          <small>${escapeHtml(auditLogSummary(item))}</small>
        </div>
        <div class="audit-meta">
          <strong>${escapeHtml(item.userName || "Sistema")}</strong>
          <small>${formatDateTime(item.createdAt)}</small>
        </div>
      </article>
    `).join("")
    : "Nenhum registro encontrado.";
}

function auditModuleLabel(module) {
  const labels = {
    auth: "Autenticação",
    product: "Produtos",
    customer: "Clientes",
    supplier: "Fornecedores",
    brand: "Marcas",
    category: "Categorias",
    user: "Usuários",
    sale: "Vendas",
    return: "Devoluções",
    cash: "Caixa",
    card_receipt: "Recebimento de cartão",
    receivable: "Crediário",
    payable: "Contas a pagar",
    backup: "Backup",
    product_photo: "Foto de produto",
    state: "Estado geral",
  };
  return labels[module] || module || "Sistema";
}

function auditActionLabel(action) {
  const labels = {
    login: "Entrou",
    logout: "Saiu",
    create: "Criou",
    update: "Editou",
    delete: "Excluiu",
    pay: "Baixou pagamento",
    cancel: "Cancelou",
    upload: "Enviou arquivo",
    replace: "Substituiu dados",
  };
  return labels[action] || action || "Alterou";
}

function auditActionIcon(action) {
  const icons = {
    login: "→",
    logout: "←",
    create: "+",
    update: "✎",
    delete: "×",
    pay: "$",
    cancel: "!",
    upload: "↑",
    replace: "↻",
  };
  return icons[action] || "•";
}

function auditLogSummary(item) {
  const details = item.details || {};
  if (item.module === "product" && details.product) return `${details.product.name || "Produto"} | ${details.product.barcode || item.refId || "-"}`;
  if (item.module === "customer" && details.customer) return details.customer.name || item.refId || "-";
  if (item.module === "supplier" && details.supplier) return details.supplier.name || item.refId || "-";
  if ((item.module === "brand" || item.module === "category") && details.name) return details.previous ? `${details.previous} para ${details.name}` : details.name;
  if (item.module === "user" && details.user) return `${details.user.name || item.refId || "-"} | ${details.user.role || "-"}`;
  if (item.module === "sale") return `${item.refId || "-"} | Total ${money.format(Number(details.total || 0))}`;
  if (item.module === "return" && details.return) return `${details.return.id || item.refId || "-"} | ${money.format(Number(details.return.total || 0))}`;
  if (item.module === "cash" && details.movement) return `${details.movement.description || item.refId || "-"} | ${money.format(Number(details.movement.amount || 0))}`;
  if (item.module === "card_receipt") return `Total registrado ${money.format(Number(details.total || 0))}`;
  if (item.module === "receivable") return `${details.customerId || item.refId || "-"} | ${money.format(Number(details.total || 0))}`;
  if (item.module === "payable" && details.payable) return `${details.payable.supplier || item.refId || "-"} | ${money.format(Number(details.payable.amount || 0))}`;
  if (item.module === "backup") return `${item.refId || details.filename || "-"} | ${formatBytes(details.size || 0)}`;
  if (item.module === "product_photo") return details.filename || item.refId || "-";
  if (item.module === "state") return "Dados gerais do sistema";
  return item.refId || "-";
}

function customerDebt(customerId) {
  const items = db.receivables.filter((item) => item.customerId === customerId && item.method === "storeCredit" && item.status !== "cancelled");
  return { open: items.reduce((total, item) => total + receivableBalance(item), 0) };
}

function receivableBalance(item) {
  if (item.status === "cancelled") return 0;
  return Math.max(0, round(item.amount - item.received));
}

function payableStatus(item) {
  if (item.status === "paid") return "paid";
  if (item.dueDate === todayIso) return "today";
  if (item.dueDate < todayIso) return "overdue";
  return "pending";
}

function findCustomerByName(name) {
  return db.customers.find((customer) => normalize(customer.name) === normalize(name));
}

function findProductFromText(text) {
  const normalized = normalize(text);
  return db.products.find((product) => normalize(product.barcode) === normalized || normalize(`${product.barcode} - ${product.name}`) === normalized || normalize(product.name) === normalized);
}

function nextCustomerCode() {
  return `CLI${String(db.customers.length + 1).padStart(5, "0")}`;
}

function nextSaleCode() {
  const max = db.sales.reduce((highest, sale) => {
    const match = String(sale.id || "").match(/^VENDA(\d+)$/i);
    return match ? Math.max(highest, Number(match[1])) : highest;
  }, 0);
  return `VENDA${String(max + 1).padStart(3, "0")}`;
}

function validCnpj(value) {
  return value.replace(/\D/g, "").length === 14;
}

function normalizePayment(value) {
  const key = normalize(value);
  if (key.includes("dinheiro")) return "cash";
  if (key.includes("pix")) return "pix";
  if (key.includes("deb")) return "debit";
  if (key.includes("cred")) return "credit";
  return "pix";
}

function datesBetween(start, end) {
  const dates = [];
  const current = new Date(`${start}T00:00:00`);
  const last = new Date(`${end}T00:00:00`);
  while (current <= last) {
    dates.push(toDateInput(current));
    current.setDate(current.getDate() + 1);
  }
  return dates;
}

function diffDays(end, start) {
  const endDate = new Date(`${end}T00:00:00`);
  const startDate = new Date(`${start}T00:00:00`);
  return Math.max(0, Math.floor((endDate - startDate) / 86400000));
}

function tableRow(title, description, value) {
  const row = document.createElement("article");
  row.className = "table-row";
  row.innerHTML = `<div><h3>${escapeHtml(title)}</h3><p>${escapeHtml(description)}</p></div><strong>${escapeHtml(value)}</strong>`;
  return row;
}

function bindChartTooltips(container) {
  container.querySelectorAll("[data-tooltip]").forEach((element) => {
    element.addEventListener("pointerenter", showChartTooltip);
    element.addEventListener("pointermove", moveChartTooltip);
    element.addEventListener("pointerleave", hideChartTooltip);
  });
}

function showChartTooltip(event) {
  const tooltip = getChartTooltip();
  tooltip.innerHTML = escapeHtml(event.currentTarget.dataset.tooltip || "").replaceAll("\n", "<br>");
  tooltip.hidden = false;
  moveChartTooltip(event);
}

function moveChartTooltip(event) {
  const tooltip = getChartTooltip();
  const offset = 14;
  tooltip.style.left = `${event.clientX + offset}px`;
  tooltip.style.top = `${event.clientY + offset}px`;
}

function hideChartTooltip() {
  getChartTooltip().hidden = true;
}

function getChartTooltip() {
  if (!chartTooltip) {
    chartTooltip = document.createElement("div");
    chartTooltip.className = "chart-tooltip";
    chartTooltip.hidden = true;
    document.body.append(chartTooltip);
  }
  return chartTooltip;
}

function button(label, className, onClick, disabled = false) {
  const element = document.createElement("button");
  element.type = "button";
  element.className = className;
  element.textContent = label;
  element.disabled = disabled;
  element.addEventListener("click", onClick);
  return element;
}

function createId() {
  return crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function readNumber(value) {
  const number = Number(String(value || "0").replace(",", "."));
  return Number.isFinite(number) ? number : 0;
}

function sum(items, field) {
  return round(items.reduce((total, item) => total + Number(item[field] || 0), 0));
}

function toCsv(rows) {
  if (!rows.length) return "";
  const headers = Object.keys(rows[0]);
  return [
    headers.join(";"),
    ...rows.map((row) => headers.map((header) => csvCell(row[header])).join(";")),
  ].join("\r\n");
}

function csvCell(value) {
  const text = String(value ?? "");
  return /[;"\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function round(value) {
  return Math.round((Number(value) + Number.EPSILON) * 100) / 100;
}

function fixed(value) {
  return Number(value || 0).toFixed(2);
}

function toDateInput(date) {
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 10);
}

function formatDate(value) {
  if (!value) return "-";
  const date = new Date(`${String(value).slice(0, 10)}T00:00:00`);
  return Number.isNaN(date.getTime()) ? "-" : new Intl.DateTimeFormat("pt-BR").format(date);
}

function timestampForDateInput(value) {
  const date = String(value || todayIso).slice(0, 10);
  const now = new Date();
  const time = [
    String(now.getHours()).padStart(2, "0"),
    String(now.getMinutes()).padStart(2, "0"),
    String(now.getSeconds()).padStart(2, "0"),
  ].join(":");
  return new Date(`${date}T${time}.${String(now.getMilliseconds()).padStart(3, "0")}`).toISOString();
}

function formatDateTime(value) {
  if (!value) return "-";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "-" : new Intl.DateTimeFormat("pt-BR", { dateStyle: "short", timeStyle: "short" }).format(date);
}

function formatBytes(value) {
  const bytes = Number(value || 0);
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1).replace(".", ",")} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1).replace(".", ",")} MB`;
}

function normalize(value) {
  return String(value || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
