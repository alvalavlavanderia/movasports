const STORAGE_KEY = "mova-sports-v1";
const OLD_KEYS = ["loja-nova-base-v1", "fashion-store-management-v2", "clothing-products-v1"];

OLD_KEYS.forEach((key) => localStorage.removeItem(key));

const todayIso = toDateInput(new Date());
const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const paymentLabels = { cash: "Dinheiro", pix: "PIX", debit: "Débito", credit: "Crédito", storeCredit: "Crediário" };
const cashExpenseTypes = ["Gasolina", "Lanches", "Estacionamento", "Motoboy", "Material de limpeza", "Outros"];
const BACKEND_ENABLED = location.protocol !== "file:";
const BACKEND_REQUIRED_MESSAGE = "O sistema precisa ser acessado pelo endereço oficial do servidor. Abra o ERP pelo link utilizado normalmente pela empresa.";
const STATE_API_URL = "/api/state";
const nativeFetch = window.fetch.bind(window);
window.fetch = (input, init = {}) => nativeFetch(input, { ...init, credentials: init.credentials || "same-origin" });
const MODULE_API_ENDPOINTS = {
  products: "/api/products",
  stockEntries: "/api/stock-entries",
  inventoryMovements: "/api/inventory-movements",
  inventories: "/api/inventories",
  supplierReturns: "/api/supplier-returns",
  supplierCredits: "/api/supplier-credits",
  customers: "/api/customers",
  suppliers: "/api/suppliers",
  brands: "/api/brands",
  categories: "/api/categories",
  sizes: "/api/sizes",
  colors: "/api/colors",
  expenseCategories: "/api/expense-categories",
  users: "/api/users",
  sales: "/api/sales",
  receivables: "/api/receivables",
  payables: "/api/payables",
  cash: "/api/cash-movements",
  returns: "/api/returns",
  exchanges: "/api/exchanges",
  warranties: "/api/warranties",
  conditionals: "/api/conditionals",
};

let db = loadDb();
let session = loadSession();
let sessionCapabilities = { dataImportReset: false };
let cart = [];
let conditionalCart = [];
let selectedConditionalId = "";
let conditionalView = "list";
let pendingConditionalSaleDraft = null;
let selectedCreditCustomerId = "";
let creditFilterStatus = "all";
let selectedPayableId = "";
let selectedCustomerDetailId = "";
let quickProductCatalogContext = null;
let returnToPayableAfterSupplier = false;
let returnToProductAfterSupplier = false;
let productPhotoData = "";
let productPhotoFile = null;
let pendingProductEntryKey = "";
let productLookupMode = "idle";
let catalogViewMode = "grid";
let serverSaveTimer = null;
let serverStateLoaded = !BACKEND_ENABLED;
let hasLocalChanges = false;
let localChangeVersion = 0;
let dashboardApiCache = null;
let dashboardApiKey = "";
let dashboardApiLoading = false;
let dashboardApiError = "";
let dashboardRequestToken = 0;
let dashboardKnownToday = storeOperationalDateKey(new Date());
let dashboardDayWatchTimer = null;
let alertsData = { items: [], pagination: {}, summary: {} };
let alertsPage = 1;
let alertsLoading = false;
let alertsLoaded = false;
let customerScoreCache = new Map();
let reportCatalog = [];
let reportCatalogLoaded = false;
let reportCatalogLoading = false;
let reportCurrentKey = "sales";
let reportCurrentData = null;
let reportCurrentRequestKey = "";
let reportLoading = false;
let reportError = "";
let reportRequestToken = 0;
let reportExporting = false;
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
let selectedInventoryProductId = "";
let selectedPhysicalInventoryId = "";
let physicalInventoryDetail = null;
let inventoryCreateKey = "";
let inventoryFinalizeKey = "";
let cardModalities = [];
let cardModalityHistory = [];
let selectedCardModalityId = "";
let cardModalitiesLoaded = false;
let saleCardModalities = [];
let saleCardModalitiesLoaded = false;
let pendingSaleKey = "";
let pendingCreditReceiptKey = "";
let pendingCreditRenegotiationKey = "";
let afterSalesMode = "return";
let afterSalesContext = null;
let afterSalesLoadTimer = null;
let exchangeItems = [];
let pendingAfterSalesKey = "";
let activeWarrantyId = "";
let payableRecurrencesChecked = false;
let cardReceivablePage = 1;
let cardReceivableData = null;
let cardReceivableLoading = false;
let cardReceivableLoadTimer = null;
let selectedCardReceivables = new Map();
let pendingCardReconciliationKey = "";
let catalogData = { items: [], total: 0, filters: {}, query: {} };
let catalogLoaded = false;
let catalogLoading = false;
let catalogError = "";
let catalogLoadTimer = null;
let generatedDocuments = [];
let generatedDocumentsLoading = false;
let documentGenerationInProgress = false;
let storeOperationalSettings = {
  storeName: "Mova Sports",
  logoUrl: "",
  paymentMethods: { cash: true, pix: true, debit: true, credit: true, storeCredit: true },
};
let storeSettings = null;
let userPreferences = { theme: "system", version: 0 };
let systemThemeListener = null;
let storeOperationalLoaded = false;
let userPreferencesLoaded = false;
let storeSettingsLoaded = false;

const els = {};
initializeAuxiliaryCatalogPanels();
document.querySelectorAll("[id]").forEach((element) => {
  els[element.id] = element;
});
let chartTooltip = null;

bindEvents();
if (!BACKEND_ENABLED) showBackendRequiredMessage();
applySession();
renderAll();
loadStoreOperationalSettings();
syncSessionFromServer();

function bindEvents() {
  document.querySelectorAll(".tab-button").forEach((button) => button.addEventListener("click", () => activateTab(button.dataset.tab)));
  document.querySelectorAll(".subtab").forEach((button) => button.addEventListener("click", () => activateSubtab(button.dataset.subtab)));
  document.querySelectorAll(".cadastro-card").forEach((button) => button.addEventListener("click", () => activateSubtab(button.dataset.subtab)));
  populateCashExpenseFilter();
  ["cashStart", "cashEnd", "reportStart", "reportEnd", "manualReceiptDate", "cancelSaleDate", "cancelSaleEndDate", "creditReceiveDate", "payableStart", "payableEnd", "bankAccountDate", "saleHistoryStart", "saleHistoryEnd"].forEach((id) => els[id].value = todayIso);
  els.storeCreditFirstDueDate.value = addCalendarMonthsIso(todayIso, 1);
  els.exchangeStoreCreditFirstDueDate.value = addCalendarMonthsIso(todayIso, 1);

  els.loginForm.addEventListener("submit", login);
  els.logoutButton.addEventListener("click", logout);
  els.productForm.addEventListener("submit", confirmProductEntry);
  els.productLookupButton.addEventListener("click", lookupProductByCode);
  els.saveProductChangesButton.addEventListener("click", saveProductChanges);
  els.productEntryQuantity.addEventListener("input", updateProductStockPreview);
  els.productBarcode.addEventListener("keydown", (event) => {
    if (event.key !== "Enter") return;
    event.preventDefault();
    lookupProductByCode();
  });
  els.productBarcode.addEventListener("input", () => {
    pendingProductEntryKey = "";
    if (els.editingProductId.value) {
      els.editingProductId.value = "";
      productLookupMode = "idle";
      updateProductMode();
    }
  });
  els.productForm.addEventListener("input", (event) => {
    if (event.target !== els.productEntryQuantity) pendingProductEntryKey = "";
  });
  els.newProductBrandButton.addEventListener("click", () => openQuickProductCatalog("brands"));
  els.newProductCategoryButton.addEventListener("click", () => openQuickProductCatalog("categories"));
  els.newProductSizeButton.addEventListener("click", () => openQuickProductCatalog("sizes"));
  els.newProductColorButton.addEventListener("click", () => openQuickProductCatalog("colors"));
  els.newProductSupplierButton.addEventListener("click", openSupplierFromProduct);
  els.clearProductButton.addEventListener("click", resetProductForm);
  els.backCadastroButton.addEventListener("click", showCadastroHome);
  els.exportProductsButton.addEventListener("click", exportProducts);
  els.exportCustomersButton.addEventListener("click", exportCustomers);
  els.productTableSearch.addEventListener("input", renderProducts);
  els.productTableFilter.addEventListener("input", renderProducts);
  els.productPhoto.addEventListener("change", readProductPhoto);
  els.productCost.addEventListener("input", updateProductMarginFromPrice);
  els.productPrice.addEventListener("input", updateProductMarginFromPrice);
  els.productMargin.addEventListener("input", updateProductPriceFromMargin);
  els.customerForm.addEventListener("submit", saveCustomer);
  els.clearCustomerButton.addEventListener("click", resetCustomerForm);
  els.newCustomerButton.addEventListener("click", resetCustomerForm);
  els.customerDetailCloseButton.addEventListener("click", closeCustomerDetail);
  els.customerDetailEditButton.addEventListener("click", () => {
    const id = selectedCustomerDetailId;
    closeCustomerDetail();
    if (id) editCustomer(id);
  });
  els.customerDetailStatusButton.addEventListener("click", () => {
    const customer = db.customers.find((item) => item.id === selectedCustomerDetailId);
    if (customer) openCustomerStatusModal(customer);
  });
  els.customerStatusForm.addEventListener("submit", saveCustomerStatus);
  els.customerStatusCloseButton.addEventListener("click", closeCustomerStatusModal);
  els.customerStatusCancelButton.addEventListener("click", closeCustomerStatusModal);
  els.supplierForm.addEventListener("submit", saveSupplier);
  els.brandForm.addEventListener("submit", (event) => saveSimpleName(event, "brands", els.brandName));
  els.categoryForm.addEventListener("submit", (event) => saveSimpleName(event, "categories", els.categoryName));
  els.sizeForm.addEventListener("submit", (event) => saveSimpleName(event, "sizes", els.sizeName));
  els.colorForm.addEventListener("submit", (event) => saveSimpleName(event, "colors", els.colorName));
  els.expenseCategoryForm.addEventListener("submit", (event) => saveSimpleName(event, "expenseCategories", els.expenseCategoryName));
  els.cardModalityForm.addEventListener("submit", saveCardModality);
  els.clearCardModalityButton.addEventListener("click", resetCardModalityForm);
  els.cardModalityType.addEventListener("change", updateCardModalityInstallments);
  els.cardModalitySearch.addEventListener("input", renderCardModalities);
  els.supplierDetailCloseButton.addEventListener("click", closeSupplierDetail);
  els.userForm.addEventListener("submit", saveUser);
  els.userThemeSelect.addEventListener("change", saveUserTheme);
  els.storeSettingsForm.addEventListener("submit", saveStoreSettings);
  els.uploadStoreLogoButton.addEventListener("click", uploadStoreLogo);

  ["customerListSearch", "customerStatusFilter", "supplierListSearch", "supplierStatusFilter", "supplierFinancialFilter", "brandListSearch", "categoryListSearch", "sizeListSearch", "colorListSearch", "expenseCategoryListSearch", "userListSearch", "stockSearch", "stockCategoryFilter", "stockBrandFilter", "stockStatusFilter", "saleProductSearch", "saleCustomerSearch", "saleDiscount", "saleAddition", "saleHistorySearch", "saleHistoryType", "saleHistoryStart", "saleHistoryEnd", "saleHistoryStatus", "cancelSaleSearch", "cancelSaleDate", "cancelSaleEndDate", "creditCustomerSearch", "payableSearch", "payableCategoryFilter", "payableFilter", "payableStart", "payableEnd", "cashStart", "cashEnd", "cashMethodFilter", "cashTypeFilter"].forEach((id) => {
    els[id].addEventListener("input", renderAll);
  });
  els.dashSalesRange.addEventListener("change", () => {
    updateDashboardPeriodControls();
    invalidateDashboardCache();
    renderDashboard();
  });
  els.dashCustomStart.addEventListener("change", invalidateDashboardCache);
  els.dashCustomEnd.addEventListener("change", invalidateDashboardCache);
  els.dashRefreshButton.addEventListener("click", () => requestDashboardSummary(true));
  els.alertBellButton.addEventListener("click", openAlertsModal);
  els.alertsCloseButton.addEventListener("click", closeAlertsModal);
  els.alertsRefreshButton.addEventListener("click", () => loadAlerts(true));
  els.alertsReadAllButton.addEventListener("click", markAllAlertsRead);
  [els.alertsSearch, els.alertsPriority, els.alertsModule, els.alertsState].forEach((element) => {
    element.addEventListener("input", () => {
      alertsPage = 1;
      loadAlerts(true);
    });
  });
  els.alertsModal.addEventListener("click", (event) => {
    if (event.target === els.alertsModal) closeAlertsModal();
  });
  els.dashboard.addEventListener("click", (event) => {
    const card = event.target.closest("[data-dashboard-action]");
    if (card) openDashboardAction(card.dataset.dashboardAction);
  });
  els.dashboard.addEventListener("keydown", (event) => {
    const card = event.target.closest("[data-dashboard-action]");
    if (!card || !["Enter", " "].includes(event.key)) return;
    event.preventDefault();
    openDashboardAction(card.dataset.dashboardAction);
  });
  window.addEventListener("focus", () => {
    if (!session) return;
    checkDashboardOperationalDay();
    invalidateDashboardCache();
    renderDashboard();
    loadAlerts(true);
  });
  startDashboardDayWatch();
  ["catalogSearch", "catalogCategoryFilter", "catalogBrandFilter", "catalogSizeFilter", "catalogColorFilter", "catalogMinPrice", "catalogMaxPrice", "catalogOrder"].forEach((id) => {
    els[id].addEventListener("input", scheduleCatalogLoad);
  });
  ["saleCustomerSearch", "saleDiscount", "saleAddition", "storeCreditInstallments", "storeCreditFirstDueDate"].forEach((id) => {
    els[id].addEventListener("input", () => {
      pendingSaleKey = "";
      renderStoreCreditDuePreview();
    });
  });
  els.saleHistoryPeriod.addEventListener("input", () => {
    updateSaleHistoryPeriodInputs();
    renderAll();
  });
  els.saleHistoryExportButton.addEventListener("click", exportSaleHistory);
  els.reportType.addEventListener("change", () => selectReport(els.reportType.value));
  els.reportPeriod.addEventListener("change", updateReportPeriodControls);
  els.reportApply.addEventListener("click", () => loadCurrentReport(true));
  els.reportExportPdf.addEventListener("click", () => exportCurrentReport("pdf"));
  els.reportExportXlsx.addEventListener("click", () => exportCurrentReport("xlsx"));
  els.reportNavigation.addEventListener("click", (event) => {
    const button = event.target.closest("[data-report-key]");
    if (button) selectReport(button.dataset.reportKey);
  });
  els.reportPagination.addEventListener("click", (event) => {
    const button = event.target.closest("[data-report-page]");
    if (!button || button.disabled) return;
    loadCurrentReport(true, Number(button.dataset.reportPage));
  });
  els.reportFeedback.addEventListener("click", (event) => {
    if (event.target.closest("[data-report-retry]")) loadCurrentReport(true);
  });
  els.reportTableBody.addEventListener("click", (event) => {
    const button = event.target.closest("[data-report-sale]");
    if (button) openReportSaleDetails(button.dataset.reportSale);
  });
  els.reportDetailClose.addEventListener("click", closeReportDetail);
  els.reportDetailModal.addEventListener("click", (event) => {
    if (event.target === els.reportDetailModal) closeReportDetail();
  });

  els.catalogPdfButton.addEventListener("click", exportCatalogPdf);
  els.catalogClearFiltersButton.addEventListener("click", clearCatalogFilters);
  els.catalogGridViewButton.addEventListener("click", () => setCatalogView("grid"));
  els.catalogListViewButton.addEventListener("click", () => setCatalogView("list"));
  els.catalogDocumentsRefreshButton.addEventListener("click", () => loadGeneratedDocuments(true));
  els.catalogDetailCloseButton.addEventListener("click", closeCatalogDetail);
  els.catalogDetailModal.addEventListener("click", (event) => {
    if (event.target === els.catalogDetailModal) closeCatalogDetail();
  });
  els.creditReceiveForm.addEventListener("submit", saveCreditReceipt);
  els.creditReceiveList.addEventListener("input", renderCreditReceiveTotal);
  ["creditReceiveDiscountType", "creditReceiveDiscountValue", "creditReceiveInterest", "creditReceiveFine", "creditReceiveAddition"].forEach((id) => {
    els[id].addEventListener("input", () => {
      pendingCreditReceiptKey = "";
      renderCreditReceiveTotal();
    });
  });
  els.creditReceiveMethod.addEventListener("input", updateCreditReceiveCardField);
  els.creditReceiveCloseButton.addEventListener("click", closeCreditReceiveModal);
  els.creditReceiveCancelButton.addEventListener("click", closeCreditReceiveModal);
  els.creditRenegotiationForm.addEventListener("submit", saveCreditRenegotiation);
  els.creditRenegotiationCloseButton.addEventListener("click", closeCreditRenegotiation);
  els.creditRenegotiationCancelButton.addEventListener("click", closeCreditRenegotiation);
  els.creditRenegotiationMethod.addEventListener("input", updateCreditRenegotiationCardField);
  ["creditRenegotiationPayment", "creditRenegotiationDiscount", "creditRenegotiationInterest", "creditRenegotiationFine", "creditRenegotiationAddition"].forEach((id) => {
    els[id].addEventListener("input", renderCreditRenegotiationTotal);
  });
  els.creditExportButton.addEventListener("click", exportCreditCustomers);
  document.querySelectorAll("[data-credit-filter]").forEach((button) => button.addEventListener("click", () => {
    creditFilterStatus = button.dataset.creditFilter;
    renderCreditCustomers();
  }));
  els.creditNewCustomerButton.addEventListener("click", () => {
    resetCustomerForm();
    activateTab("cadastros");
    activateSubtab("cad-cliente");
  });
  els.stockExportButton.addEventListener("click", exportProducts);
  els.inventoryHistoryClear.addEventListener("click", () => {
    selectedInventoryProductId = "";
    renderInventoryHistory();
  });
  els.stockNewProductButton.addEventListener("click", () => {
    resetProductForm();
    activateTab("cadastros");
    activateSubtab("cad-produto");
  });
  els.newInventoryButton.addEventListener("click", openInventoryCreate);
  els.inventoryCreateCloseButton.addEventListener("click", closeInventoryCreate);
  els.inventoryCreateCancelButton.addEventListener("click", closeInventoryCreate);
  els.inventoryType.addEventListener("input", updateInventoryCreateFields);
  els.inventoryCreateForm.addEventListener("submit", createPhysicalInventory);
  els.inventorySearch.addEventListener("input", renderPhysicalInventories);
  els.inventoryTypeFilter.addEventListener("input", renderPhysicalInventories);
  els.inventoryStatusFilter.addEventListener("input", renderPhysicalInventories);
  els.inventoryUserFilter.addEventListener("input", renderPhysicalInventories);
  els.inventoryStartFilter.addEventListener("input", renderPhysicalInventories);
  els.inventoryEndFilter.addEventListener("input", renderPhysicalInventories);
  els.inventoryBackButton.addEventListener("click", closeInventoryDetail);
  els.inventoryBarcodeForm.addEventListener("submit", countInventoryBarcode);
  els.inventoryItemFilter.addEventListener("input", renderPhysicalInventoryDetail);
  els.inventoryFinalizeButton.addEventListener("click", finalizePhysicalInventory);
  els.inventoryCancelButton.addEventListener("click", cancelPhysicalInventory);
  els.clearSaleButton.addEventListener("click", clearSale);
  els.addPaymentButton.addEventListener("click", () => addPaymentRow("cash"));
  els.finishSaleButton.addEventListener("click", finishSale);
  els.saleItemAdjustmentForm.addEventListener("submit", saveSaleItemAdjustment);
  els.saleItemAdjustmentCloseButton.addEventListener("click", closeSaleItemAdjustment);
  els.saleItemAdjustmentCancelButton.addEventListener("click", closeSaleItemAdjustment);
  els.conditionalProductSearch.addEventListener("input", renderConditionalProducts);
  els.conditionalOpenSearch.addEventListener("input", renderConditionalOpenList);
  els.conditionalStatusFilter.addEventListener("input", renderConditionalOpenList);
  els.conditionalStartFilter.addEventListener("input", renderConditionalOpenList);
  els.conditionalEndFilter.addEventListener("input", renderConditionalOpenList);
  els.newConditionalButton.addEventListener("click", startNewConditional);
  els.clearConditionalButton.addEventListener("click", clearConditional);
  els.sendConditionalButton.addEventListener("click", saveConditional);
  els.returnForm.addEventListener("submit", submitAfterSales);
  els.returnProductSearch.addEventListener("input", scheduleAfterSalesLoad);
  document.querySelectorAll("[data-after-sales-mode]").forEach((button) => {
    button.addEventListener("click", () => setAfterSalesMode(button.dataset.afterSalesMode));
  });
  els.addExchangeProductButton.addEventListener("click", addExchangeProduct);
  els.addExchangePaymentButton.addEventListener("click", () => addExchangePaymentRow());
  els.exchangeStoreCreditInstallments.addEventListener("input", () => {
    pendingAfterSalesKey = "";
  });
  els.exchangeStoreCreditFirstDueDate.addEventListener("input", () => {
    pendingAfterSalesKey = "";
  });
  els.clearAfterSalesButton.addEventListener("click", clearAfterSalesForm);
  els.manualReceiptForm.addEventListener("submit", saveManualReceipt);
  els.manualReceiptForm.addEventListener("input", renderManualReceiptSummary);
  els.payableForm.addEventListener("submit", savePayable);
  els.payableNewSupplierButton.addEventListener("click", openSupplierFromPayable);
  els.payableNewButton.addEventListener("click", openNewPayableForm);
  els.payableRecurring.addEventListener("input", updatePayableRecurrenceField);
  els.payablePaymentForm.addEventListener("submit", savePayablePayment);
  els.payablePaymentCloseButton.addEventListener("click", closePayablePaymentModal);
  els.payablePaymentCancelButton.addEventListener("click", closePayablePaymentModal);
  els.payablePaymentInterest.addEventListener("input", renderPayablePaymentTotal);
  els.payablePaymentFine.addEventListener("input", renderPayablePaymentTotal);
  els.payablePaymentDiscount.addEventListener("input", renderPayablePaymentTotal);
  els.payablePaymentAmount.addEventListener("input", renderPayablePaymentTotal);
  document.querySelectorAll("[data-payable-filter]").forEach((button) => button.addEventListener("click", () => {
    els.payableFilter.value = button.dataset.payableFilter;
    renderAll();
  }));
  els.bankAccountButton.addEventListener("click", () => activateTab("cartoes"));
  els.bankAccountForm.addEventListener("submit", saveBankAccountEntry);
  els.cashMovementButton.addEventListener("click", () => els.cashMovementPanel.hidden = !els.cashMovementPanel.hidden);
  els.cashMovementType.addEventListener("input", updateCashExpenseField);
  els.cashMovementForm.addEventListener("submit", saveCashMovement);
  els.cashExportButton.addEventListener("click", exportCashMovements);
  els.cardReceivableSearch.addEventListener("input", scheduleCardReceivablesLoad);
  ["cardReceivableMethod", "cardReceivableStatus", "cardReceivableStart", "cardReceivableEnd"].forEach((id) => {
    els[id].addEventListener("input", () => loadCardReceivables(true));
  });
  els.cardReconcileSelectedButton.addEventListener("click", openCardReconciliation);
  els.cardReconciliationForm.addEventListener("submit", submitCardReconciliation);
  els.cardReconciliationItems.addEventListener("input", updateCardReconciliationTotals);
  els.cardReconciliationTotal.addEventListener("input", updateCardReconciliationTotals);
  els.cardReconciliationCloseButton.addEventListener("click", closeCardReconciliation);
  els.cardReconciliationCancelButton.addEventListener("click", closeCardReconciliation);
  els.cardReceivableDetailCloseButton.addEventListener("click", closeCardReceivableDetail);
  els.refreshDatabaseButton.addEventListener("click", () => loadDatabaseStatus(true));
  els.refreshBackupsButton.addEventListener("click", () => loadBackups(true));
  els.createBackupButton.addEventListener("click", createBackup);
  els.exportDataButton.addEventListener("click", exportSystemData);
  els.importDataButton.addEventListener("click", importSystemData);
  els.resetDataButton.addEventListener("click", resetSystemData);
  els.refreshAuditButton.addEventListener("click", () => loadAuditLogs(true));
  els.changePasswordForm.addEventListener("submit", changePassword);
  ["cashExpenseFilter"].forEach((id) => els[id].addEventListener("input", renderCash));
  ["auditSearch"].forEach((id) => els[id].addEventListener("input", renderAuditLogs));
  ["auditModuleFilter", "auditActionFilter", "auditLimit"].forEach((id) => els[id].addEventListener("input", () => loadAuditLogs(true)));
  updateCashExpenseField();
  updatePayableRecurrenceField();
}

function populateCashExpenseFilter() {
  const catalogItems = activeCatalogItems("expenseCategories").map(catalogName);
  const types = catalogItems.length ? catalogItems : cashExpenseTypes;
  if (els.cashExpenseFilter) {
    const current = els.cashExpenseFilter.value || "all";
    els.cashExpenseFilter.innerHTML = ['<option value="all">Todos</option>', ...types.map((type) => `<option value="${escapeHtml(type)}">${escapeHtml(type)}</option>`)].join("");
    els.cashExpenseFilter.value = types.includes(current) || current === "all" ? current : "all";
  }
  if (els.cashExpenseType) {
    const current = els.cashExpenseType.value;
    els.cashExpenseType.innerHTML = ['<option value="">Selecione...</option>', ...types.map((type) => `<option value="${escapeHtml(type)}">${escapeHtml(type)}</option>`)].join("");
    els.cashExpenseType.value = types.includes(current) ? current : "";
  }
}

function updateCashExpenseField() {
  if (!els.cashExpenseTypeField || !els.cashExpenseType) return;
  const isOut = els.cashMovementType.value === "out";
  els.cashExpenseTypeField.hidden = !isOut;
  els.cashExpenseType.required = isOut;
  if (!isOut) els.cashExpenseType.value = "";
  const currentMethod = els.cashMovementMethod.value;
  const methods = isOut
    ? [["cash", "Dinheiro"], ["pix", "PIX"], ["debit", "Débito"]]
    : [["cash", "Dinheiro"], ["pix", "PIX"]];
  els.cashMovementMethod.innerHTML = methods
    .map(([value, label]) => `<option value="${value}">${label}</option>`)
    .join("");
  els.cashMovementMethod.value = methods.some(([value]) => value === currentMethod)
    ? currentMethod
    : "cash";
}

function initializeAuxiliaryCatalogPanels() {
  const configurations = {
    sizes: { singular: "Tamanho", plural: "Tamanhos", prefix: "size" },
    colors: { singular: "Cor", plural: "Cores", prefix: "color" },
    expenseCategories: {
      singular: "Categoria de despesa",
      plural: "Categorias de despesa",
      prefix: "expenseCategory",
    },
  };
  document.querySelectorAll(".auxiliary-catalog-panel").forEach((panel) => {
    const config = configurations[panel.dataset.catalogKind];
    if (!config) return;
    panel.innerHTML = `
      <div class="cadastro-register-layout compact-register">
        <section class="panel cadastro-form-card">
          <div class="section-title"><h2>Informações de ${config.singular}</h2></div>
          <form id="${config.prefix}Form" class="cadastro-form-grid">
            <input id="editing${config.prefix[0].toUpperCase()}${config.prefix.slice(1)}Id" type="hidden">
            <label class="field span-3">Nome<input id="${config.prefix}Name" type="text" required></label>
            <button class="primary span-3" type="submit">Salvar ${config.singular}</button>
          </form>
        </section>
        <section class="panel cadastro-list-card">
          <div class="section-title"><h2>${config.plural} cadastrados</h2></div>
          <div class="cadastro-list-toolbar">
            <input id="${config.prefix}ListSearch" type="search" placeholder="Buscar ${config.singular.toLowerCase()}...">
          </div>
          <div class="cadastro-table-wrap">
            <table class="cadastro-table simple-cadastro-table">
              <thead><tr><th>${config.singular}</th><th>Situação</th><th>Ações</th></tr></thead>
              <tbody id="${config.prefix}List"></tbody>
            </table>
          </div>
        </section>
      </div>
    `;
  });
}

function catalogName(item) {
  return typeof item === "string" ? item : String(item?.name || "");
}

function normalizeCatalogCollection(items = [], collection = "catalog") {
  return items
    .map((item) => typeof item === "string"
      ? { id: `legacy:${collection}:${normalize(item).replace(/\s+/g, "-")}`, name: item, status: "active" }
      : { ...item, name: catalogName(item), status: item?.status || "active" })
    .filter((item) => item.name);
}

function activeCatalogItems(collection) {
  return (db[collection] || []).filter((item) => item.status !== "deactivated");
}

function findCatalogItem(collection, name) {
  const normalized = normalize(name);
  return activeCatalogItems(collection).find((item) => normalize(item.name) === normalized);
}

function defaultDb() {
  return {
    users: [],
    products: [],
    stockEntries: [],
    stockMovements: [],
    inventoryMovements: [],
    inventories: [],
    supplierReturns: [],
    supplierCredits: [],
    customers: [],
    suppliers: [],
    brands: [],
    categories: [],
    sizes: [],
    colors: [],
    expenseCategories: [],
    sales: [],
    receivables: [],
    payables: [],
    cash: [],
    cashClosings: [],
    returns: [],
    exchanges: [],
    warranties: [],
    conditionals: [],
  };
}

function sanitizeUserForBrowser(user = {}) {
  const { password, password_hash, passwordHash, ...publicUser } = user;
  void password;
  void password_hash;
  void passwordHash;
  return publicUser;
}

function browserSafeDb(data = {}) {
  return {
    ...data,
    users: Array.isArray(data.users) ? data.users.map(sanitizeUserForBrowser) : [],
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
  db = browserSafeDb(db);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(db));
  invalidateDashboardCache();
  if (!BACKEND_ENABLED) {
    hasLocalChanges = true;
    localChangeVersion += 1;
  }
}

function persistLocalOnly() {
  db = browserSafeDb(db);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(db));
  invalidateDashboardCache();
}

function invalidateDashboardCache() {
  dashboardApiCache = null;
  dashboardApiKey = "";
  dashboardApiError = "";
  dashboardRequestToken += 1;
  reportCurrentData = null;
  reportCurrentRequestKey = "";
  reportError = "";
  reportRequestToken += 1;
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
  const endpoints = Object.entries(MODULE_API_ENDPOINTS)
    .filter(([key]) => key !== "users" || isAdmin());
  const entries = await Promise.all(endpoints.map(async ([key, url]) => {
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
  return (users || []).map(sanitizeUserForBrowser);
}

function applyServerDb(serverDb) {
  db = browserSafeDb(serverDb);
  if (!isAdmin()) db.users = [];
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
  ["brands", "categories", "sizes", "colors", "expenseCategories"].forEach((collection) => {
    merged[collection] = normalizeCatalogCollection(merged[collection], collection);
  });
  merged.users = merged.users.map(sanitizeUserForBrowser);
  return browserSafeDb(merged);
}

function hasBusinessData(data) {
  return ["products", "customers", "suppliers", "brands", "categories", "sales", "receivables", "payables", "cash", "returns", "exchanges", "warranties", "conditionals"].some((key) => data?.[key]?.length);
}

function scheduleServerPersist() {
  return;
}

async function saveStateToServer(version = localChangeVersion) {
  void version;
  return false;
}

function loadSession() {
  return null;
}

function saveSession() {
  // A sessao autenticada pertence ao cookie HTTP gerenciado pelo Flask.
}

function setSessionCapabilities(capabilities) {
  sessionCapabilities = {
    dataImportReset: capabilities?.dataImportReset === true,
  };
}

function clearSessionCapabilities() {
  setSessionCapabilities(null);
  cardModalities = [];
  cardModalityHistory = [];
  selectedCardModalityId = null;
  cardModalitiesLoaded = false;
  saleCardModalities = [];
  saleCardModalitiesLoaded = false;
  pendingSaleKey = "";
  window.clearTimeout(cardReceivableLoadTimer);
  cardReceivableLoadTimer = null;
  cardReceivableData = null;
  cardReceivableLoading = false;
  cardReceivablePage = 1;
  selectedCardReceivables.clear();
  pendingCardReconciliationKey = "";
  alertsData = { items: [], pagination: {}, summary: {} };
  alertsPage = 1;
  alertsLoaded = false;
  customerScoreCache.clear();
  if (els.alertBellCount) {
    els.alertBellCount.hidden = true;
    els.alertBellCount.textContent = "0";
  }
}

function canImportOrResetData() {
  return Boolean(session && isAdmin() && sessionCapabilities.dataImportReset);
}

function showBackendRequiredMessage() {
  els.loginMessage.textContent = BACKEND_REQUIRED_MESSAGE;
  els.loginMessage.hidden = false;
}

async function login(event) {
  event.preventDefault();
  els.loginMessage.hidden = true;
  clearSessionCapabilities();
  applySession();
  if (!BACKEND_ENABLED) {
    showBackendRequiredMessage();
    return;
  }
  try {
    const response = await fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ login: els.loginUser.value.trim(), password: els.loginPassword.value }),
    });
    const payload = await response.json();
    if (response.ok && payload.user) {
      session = sanitizeUserForBrowser(payload.user);
      setSessionCapabilities(payload.capabilities);
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
    session = null;
    applySession();
    showBackendRequiredMessage();
  }
}

async function logout() {
  session = null;
  clearSessionCapabilities();
  saveSession();
  applySession();
  if (BACKEND_ENABLED) {
    try {
      await fetch("/api/logout", { method: "POST" });
    } catch (error) {
      console.warn(error);
    }
  }
}

async function syncSessionFromServer() {
  if (!BACKEND_ENABLED) return;
  try {
    const response = await fetch("/api/session", { cache: "no-store" });
    if (!response.ok) {
      session = null;
      clearSessionCapabilities();
      saveSession();
      applySession();
      return;
    }
    const payload = await response.json();
    if (payload.user) {
      session = sanitizeUserForBrowser(payload.user);
      setSessionCapabilities(payload.capabilities);
      saveSession();
      applySession();
      await syncFromServer();
      renderAll();
    } else {
      session = null;
      clearSessionCapabilities();
      saveSession();
      applySession();
      renderAll();
    }
  } catch (error) {
    clearSessionCapabilities();
    applySession();
    console.warn(error);
  }
}

function applySelectedTheme(theme = "system") {
  const media = window.matchMedia("(prefers-color-scheme: dark)");
  const effective = theme === "system" ? (media.matches ? "dark" : "light") : theme;
  document.documentElement.dataset.theme = effective;
  if (systemThemeListener) {
    media.removeEventListener?.("change", systemThemeListener);
    systemThemeListener = null;
  }
  if (theme === "system") {
    systemThemeListener = () => applySelectedTheme("system");
    media.addEventListener?.("change", systemThemeListener);
  }
  if (els.userThemeSelect) els.userThemeSelect.value = theme;
}

async function loadUserPreferences(force = false) {
  if (!session || !BACKEND_ENABLED || (userPreferencesLoaded && !force)) return;
  try {
    const response = await fetch("/api/me/preferences", { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      throw new Error(payload.error || "Não foi possível carregar suas preferências.");
    }
    userPreferences = payload.data || { theme: "system", version: 0 };
    userPreferencesLoaded = true;
    applySelectedTheme(userPreferences.theme);
  } catch (error) {
    console.warn(error);
    applySelectedTheme("system");
  }
}

async function saveUserTheme() {
  const theme = els.userThemeSelect.value;
  applySelectedTheme(theme);
  if (!session || !BACKEND_ENABLED) return;
  try {
    const response = await fetch("/api/me/preferences", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ theme, expectedVersion: userPreferences.version || 0 }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      await loadUserPreferences(true);
      return alert(payload.error || "Não foi possível salvar a aparência.");
    }
    userPreferences = payload.data;
    userPreferencesLoaded = true;
  } catch (error) {
    console.warn(error);
    await loadUserPreferences(true);
    alert("Não foi possível conectar ao servidor para salvar a aparência.");
  }
}

function applyStoreIdentity(settings) {
  if (!settings) return;
  const name = settings.storeName || "Mova Sports";
  document.title = name;
  els.brandLogo.alt = name;
  if (settings.logoUrl) els.brandLogo.src = settings.logoUrl;
}

async function loadStoreOperationalSettings(force = false) {
  if (!BACKEND_ENABLED || (storeOperationalLoaded && !force)) return;
  try {
    const response = await fetch("/api/store/operational-settings", { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      throw new Error(payload.error || "Não foi possível carregar os dados da loja.");
    }
    storeOperationalSettings = payload.data || storeOperationalSettings;
    storeOperationalLoaded = true;
    applyStoreIdentity(storeOperationalSettings);
    refreshSalePaymentMethods();
  } catch (error) {
    console.warn(error);
  }
}

function renderStoreSettings(settings) {
  if (!settings) return;
  const fieldMap = {
    storeName: "storeName", legalName: "storeLegalName", tradeName: "storeTradeName",
    document: "storeDocument", phone: "storePhone", whatsapp: "storeWhatsapp",
    email: "storeEmail", zip: "storeZip", address: "storeAddress",
    addressNumber: "storeAddressNumber", complement: "storeComplement",
    district: "storeDistrict", city: "storeCity", state: "storeState",
    receiptFooter: "storeReceiptFooter",
  };
  Object.entries(fieldMap).forEach(([key, id]) => { els[id].value = settings[key] || ""; });
  els.storeSettingsVersion.value = String(settings.version || 0);
  els.printShowDocument.checked = Boolean(settings.printPreferences?.showDocument);
  els.printShowPhone.checked = Boolean(settings.printPreferences?.showPhone);
  els.printShowWhatsapp.checked = Boolean(settings.printPreferences?.showWhatsapp);
  els.printShowAddress.checked = Boolean(settings.printPreferences?.showAddress);
  els.printShowEmail.checked = Boolean(settings.printPreferences?.showEmail);
  els.storePixKey.value = settings.pix?.key || "";
  els.storePixKeyType.value = settings.pix?.keyType || "";
  els.storePixRecipientName.value = settings.pix?.recipientName || "";
  els.storePixRecipientDocument.value = settings.pix?.recipientDocument || "";
  els.storePixBank.value = settings.pix?.bank || "";
  els.paymentPixEnabled.checked = Boolean(settings.paymentMethods?.pix);
  els.paymentDebitEnabled.checked = Boolean(settings.paymentMethods?.debit);
  els.paymentCreditEnabled.checked = Boolean(settings.paymentMethods?.credit);
  els.paymentStoreCreditEnabled.checked = Boolean(settings.paymentMethods?.storeCredit);
  els.storeLogoPreview.hidden = !settings.logoUrl;
  if (settings.logoUrl) els.storeLogoPreview.src = settings.logoUrl;
  els.storeSettingsStatus.textContent = settings.updatedAt
    ? `Atualizado em ${formatDateTime(settings.updatedAt)}.`
    : "Configuração padrão ainda não salva.";
}

async function loadStoreSettings(force = false) {
  if (!isAdmin() || !BACKEND_ENABLED || (storeSettingsLoaded && !force)) return;
  try {
    const response = await fetch("/api/settings/store", { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      throw new Error(payload.error || "Não foi possível carregar as configurações.");
    }
    storeSettings = payload.data;
    storeSettingsLoaded = true;
    renderStoreSettings(storeSettings);
  } catch (error) {
    console.warn(error);
    els.storeSettingsStatus.textContent = "Não foi possível carregar as configurações.";
  }
}

function storeSettingsPayload() {
  return {
    expectedVersion: Number(els.storeSettingsVersion.value || 0),
    storeName: els.storeName.value,
    legalName: els.storeLegalName.value,
    tradeName: els.storeTradeName.value,
    document: els.storeDocument.value,
    phone: els.storePhone.value,
    whatsapp: els.storeWhatsapp.value,
    email: els.storeEmail.value,
    zip: els.storeZip.value,
    address: els.storeAddress.value,
    addressNumber: els.storeAddressNumber.value,
    complement: els.storeComplement.value,
    district: els.storeDistrict.value,
    city: els.storeCity.value,
    state: els.storeState.value,
    receiptFooter: els.storeReceiptFooter.value,
    printPreferences: {
      showDocument: els.printShowDocument.checked,
      showPhone: els.printShowPhone.checked,
      showWhatsapp: els.printShowWhatsapp.checked,
      showAddress: els.printShowAddress.checked,
      showEmail: els.printShowEmail.checked,
    },
    pix: {
      key: els.storePixKey.value,
      keyType: els.storePixKeyType.value,
      recipientName: els.storePixRecipientName.value,
      recipientDocument: els.storePixRecipientDocument.value,
      bank: els.storePixBank.value,
    },
    paymentMethods: {
      cash: true,
      pix: els.paymentPixEnabled.checked,
      debit: els.paymentDebitEnabled.checked,
      credit: els.paymentCreditEnabled.checked,
      storeCredit: els.paymentStoreCreditEnabled.checked,
    },
  };
}

async function saveStoreSettings(event) {
  event.preventDefault();
  els.storeSettingsStatus.textContent = "Salvando configurações...";
  try {
    const response = await fetch("/api/settings/store", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(storeSettingsPayload()),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      if (response.status === 409) await loadStoreSettings(true);
      return alert(payload.error || "Não foi possível salvar as configurações.");
    }
    storeSettings = payload.data;
    storeSettingsLoaded = true;
    renderStoreSettings(storeSettings);
    storeOperationalLoaded = false;
    await loadStoreOperationalSettings(true);
  } catch (error) {
    console.warn(error);
    els.storeSettingsStatus.textContent = "Falha de conexão ao salvar.";
  }
}

async function uploadStoreLogo() {
  const file = els.storeLogoFile.files?.[0];
  if (!file) return alert("Selecione uma imagem para a logo.");
  const data = new FormData();
  data.append("photo", file);
  data.append("expectedVersion", els.storeSettingsVersion.value || "0");
  try {
    const response = await fetch("/api/settings/store/logo", { method: "POST", body: data });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      if (response.status === 409) await loadStoreSettings(true);
      return alert(payload.error || "Não foi possível enviar a logo.");
    }
    storeSettings = payload.data;
    storeSettingsLoaded = true;
    els.storeLogoFile.value = "";
    renderStoreSettings(storeSettings);
    storeOperationalLoaded = false;
    await loadStoreOperationalSettings(true);
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para enviar a logo.");
  }
}

async function loadAccessMatrix() {
  if (!isAdmin() || !BACKEND_ENABLED) return;
  try {
    const response = await fetch("/api/settings/access-matrix", { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.error || "Não foi possível carregar os acessos.");
    els.accessMatrixList.innerHTML = (payload.data?.permissions || []).map((item) => `
      <tr>
        <td><strong>${escapeHtml(item.label)}</strong></td>
        <td>${item.admin ? "Permitido" : "Sem acesso"}</td>
        <td>${item.operator ? "Permitido" : "Sem acesso"}</td>
      </tr>
    `).join("") || `<tr><td colspan="3" class="empty-cell">Nenhum acesso configurado.</td></tr>`;
  } catch (error) {
    console.warn(error);
    els.accessMatrixList.innerHTML = `<tr><td colspan="3" class="empty-cell">Não foi possível carregar os acessos.</td></tr>`;
  }
}

function applySession() {
  const logged = Boolean(session);
  const allowDataOperations = logged && canImportOrResetData();
  if (!logged) {
    payableRecurrencesChecked = false;
    catalogLoaded = false;
    catalogData = { items: [], total: 0, filters: {}, query: {} };
    generatedDocuments = [];
    reportCatalog = [];
    reportCatalogLoaded = false;
    reportCurrentData = null;
    reportCurrentRequestKey = "";
    reportError = "";
    storeOperationalLoaded = false;
    userPreferencesLoaded = false;
    storeSettingsLoaded = false;
    storeSettings = null;
    applySelectedTheme("system");
  }
  els.loginScreen.hidden = logged;
  els.currentUserLabel.textContent = logged ? session.name : "";
  els.currentUserRole.textContent = logged ? (session.role === "admin" ? "Administrador" : "Operador") : "";
  document.querySelectorAll(".admin-only").forEach((element) => element.hidden = session?.role !== "admin");
  document.querySelectorAll(".manager-only").forEach((element) => element.hidden = session?.role !== "admin");
  if (els.importDataPanel) els.importDataPanel.hidden = !allowDataOperations;
  if (els.resetDataPanel) els.resetDataPanel.hidden = !allowDataOperations;
  if (logged) loadSaleCardModalities();
  if (logged) loadAlerts();
  if (logged) loadStoreOperationalSettings();
  if (logged) loadUserPreferences();
}

function handleUnauthorized(response, payload = {}) {
  if (response.status !== 401) return false;
  session = null;
  clearSessionCapabilities();
  saveSession();
  applySession();
  alert(payload.error || "Sua sessão expirou. Faça login novamente.");
  return true;
}

function isAdmin() {
  return session?.role === "admin";
}

function activateTab(tabId) {
  document.querySelectorAll(".tab-button").forEach((button) => button.classList.toggle("active", button.dataset.tab === tabId));
  document.querySelectorAll(".tab-panel").forEach((panel) => panel.classList.toggle("active", panel.id === tabId));
  if (tabId === "cadastros") showCadastroHome();
  if (tabId === "configuracoes") {
    loadStoreSettings();
    loadAccessMatrix();
    loadDatabaseStatus();
    loadBackups();
    loadAuditLogs(true);
  }
  if (tabId === "contas") ensurePayableRecurrences();
  if (tabId === "cartoes") loadCardReceivables();
  if (tabId === "catalogo") {
    loadCatalog(true);
    loadGeneratedDocuments();
  }
  if (tabId === "relatorios") loadReportCatalog();
  if (tabId === "dashboard") {
    invalidateDashboardCache();
    renderDashboard();
    loadAlerts(true);
  }
}

function activateSubtab(tabId) {
  const parent = document.getElementById(tabId).closest(".tab-panel");
  parent.querySelectorAll(".subtab").forEach((button) => button.classList.toggle("active", button.dataset.subtab === tabId));
  parent.querySelectorAll(".subtab-panel").forEach((panel) => panel.classList.toggle("active", panel.id === tabId));
  updateCadastroHeader(tabId);
  updateSaleHeader(tabId);
  if (tabId === "cad-modalidade") loadCardModalities();
  if (tabId === "nova-venda") loadSaleCardModalities();
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
    "cad-tamanho": ["Cadastro de Tamanhos", "Padronize os tamanhos dos produtos."],
    "cad-cor": ["Cadastro de Cores", "Padronize as cores dos produtos."],
    "cad-despesa": ["Categorias de Despesa", "Organize despesas do caixa e contas a pagar."],
    "cad-modalidade": ["Modalidades de Cartão", "Gerencie taxas, prazos e vigências."],
    "cad-usuario": ["Cadastro de Usuários", "Gerencie acessos e permissões do sistema."],
  };
  const [title, subtitle] = labels[tabId] || labels["cad-home"];
  els.cadastroTitle.textContent = title;
  els.cadastroSubtitle.textContent = subtitle;
  const crumbs = {
    "cad-home": "Cadastros",
    "cad-produto": "Produto",
    "cad-cliente": "Cliente",
    "cad-fornecedor": "Fornecedor",
    "cad-marca": "Marca",
    "cad-categoria": "Categoria",
    "cad-tamanho": "Tamanho",
    "cad-cor": "Cor",
    "cad-despesa": "Categoria de despesa",
    "cad-modalidade": "Modalidades de Cartão",
    "cad-usuario": "Usuários",
  };
  const crumb = crumbs[tabId] || "Cadastros";
  els.cadastroTitle.textContent = crumb === "Cadastros" ? "Mova Sports | Cadastros" : `Mova Sports | Cadastros | ${crumb}`;
  els.cadastroSubtitle.hidden = true;
  els.cadastroPageActions.hidden = tabId === "cad-home";
  document.querySelectorAll(".product-only-action").forEach((element) => element.hidden = tabId !== "cad-produto");
  document.querySelectorAll(".customer-only-action").forEach((element) => element.hidden = tabId !== "cad-cliente");
}

function updateSaleHeader(tabId) {
  if (!els.saleBreadcrumbTitle) return;
  const labels = {
    "nova-venda": "Nova venda",
    condicional: "Condicional",
    devolucao: "Devolução/troca",
    "historico-vendas": "Histórico",
    "cancelar-venda": "Cancelar venda",
  };
  if (!labels[tabId]) return;
  els.saleBreadcrumbTitle.textContent = `Mova Sports | Vendas | ${labels[tabId]}`;
}

function updateProductMarginFromPrice() {
  const cost = readNumber(els.productCost.value);
  const price = readNumber(els.productPrice.value);
  const margin = cost > 0 ? ((price - cost) / cost) * 100 : 0;
  els.productMargin.value = fixed(margin);
}

function updateProductPriceFromMargin() {
  const cost = readNumber(els.productCost.value);
  const margin = readNumber(els.productMargin.value);
  const price = cost > 0 ? cost * (1 + margin / 100) : 0;
  els.productPrice.value = fixed(price);
}

async function productPayloadFromForm(existing = null) {
  const photo = await resolveProductPhoto(existing?.photo || "");
  if (photo === null) return null;
  return {
    barcode: els.productBarcode.value.trim().toUpperCase(),
    name: els.productName.value.trim(),
    size: els.productSize.value.trim(),
    sizeId: findCatalogItem("sizes", els.productSize.value)?.id || "",
    color: els.productColor.value.trim(),
    colorId: findCatalogItem("colors", els.productColor.value)?.id || "",
    gender: els.productGender.value,
    category: els.productCategory.value.trim(),
    categoryId: findCatalogItem("categories", els.productCategory.value)?.id || "",
    brand: els.productBrand.value.trim(),
    brandId: findCatalogItem("brands", els.productBrand.value)?.id || "",
    supplier: els.productSupplier.value.trim(),
    supplierId: db.suppliers.find((item) => item.status === "active" && normalize(item.name) === normalize(els.productSupplier.value))?.id || "",
    minStock: Math.max(0, Math.floor(readNumber(els.productMinStock.value))),
    description: els.productDescription.value.trim(),
    active: els.productActive.checked,
    cost: readNumber(els.productCost.value),
    price: readNumber(els.productPrice.value),
    photo,
  };
}

async function responsePayload(response) {
  const raw = await response.text();
  try {
    return raw ? JSON.parse(raw) : {};
  } catch {
    return { error: raw ? raw.slice(0, 180) : "" };
  }
  if (tabId === "inventario") renderPhysicalInventories();
}

function setProductStockSummary(product = null) {
  const real = Math.max(0, Number(product?.stock || 0));
  const reserved = Math.max(0, Number(product?.reservedStock || 0));
  const available = Math.max(0, Number(product?.availableStock ?? real - reserved));
  els.productRealStock.textContent = String(real);
  els.productReservedStock.textContent = String(reserved);
  els.productAvailableStock.textContent = String(available);
  updateProductStockPreview();
}

function updateProductStockPreview() {
  const real = Math.max(0, Number(els.productRealStock?.textContent || 0));
  const quantity = Number(els.productEntryQuantity?.value || 0);
  els.productStockAfter.value = Number.isInteger(quantity) && quantity > 0 ? String(real + quantity) : "";
}

function updateProductMode() {
  const existing = db.products.find((item) => item.id === els.editingProductId.value);
  els.saveProductChangesButton.hidden = !existing;
  els.confirmProductEntryButton.textContent = existing ? "Confirmar entrada" : "Cadastrar e dar entrada";
  if (productLookupMode === "existing" && existing) {
    els.productLookupStatus.textContent = existing.active === false
      ? "Produto já cadastrado e desativado. Reative-o antes da entrada."
      : "Produto já cadastrado. Você pode editar os dados ou confirmar uma nova entrada.";
    els.productLookupStatus.dataset.state = existing.active === false ? "warning" : "found";
  } else if (productLookupMode === "new") {
    els.productLookupStatus.textContent = "Código ainda não cadastrado. Preencha os dados e registre a primeira entrada.";
    els.productLookupStatus.dataset.state = "new";
  } else {
    els.productLookupStatus.textContent = "Informe ou leia o código para começar.";
    els.productLookupStatus.dataset.state = "idle";
  }
  renderProductEntryHistory(existing?.id || "");
}

function populateProductForm(product) {
  els.editingProductId.value = product.id;
  els.productBarcode.value = product.barcode;
  els.productName.value = product.name;
  els.productSize.value = product.size || "";
  els.productColor.value = product.color || "";
  els.productGender.value = product.gender || "Feminino";
  els.productCategory.value = product.category || "";
  els.productBrand.value = product.brand || "";
  els.productSupplier.value = product.supplier || "";
  els.productMinStock.value = product.minStock || 0;
  els.productDescription.value = product.description || "";
  els.productActive.checked = product.active !== false;
  els.productCost.value = fixed(product.cost);
  els.productPrice.value = fixed(product.price);
  els.productEntryQuantity.value = "1";
  updateProductMarginFromPrice();
  productPhotoData = product.photo || "";
  productPhotoFile = null;
  setProductStockSummary(product);
  productLookupMode = "existing";
  updateProductMode();
}

async function lookupProductByCode() {
  const barcode = els.productBarcode.value.trim().toUpperCase();
  if (!barcode) return alert("Informe o código do produto.");
  if (!BACKEND_ENABLED) return showBackendRequiredMessage();
  els.productLookupButton.disabled = true;
  els.productLookupStatus.textContent = "Consultando produto...";
  els.productLookupStatus.dataset.state = "loading";
  try {
    const response = await fetch(`/api/products/lookup?barcode=${encodeURIComponent(barcode)}`, { cache: "no-store" });
    const payload = await responsePayload(response);
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return false;
      alert(payload.error || "Não foi possível consultar o produto.");
      productLookupMode = "idle";
      updateProductMode();
      return false;
    }
    if (payload.data?.exists && payload.data.product) {
      applyProductLocally(payload.data.product);
      populateProductForm(payload.data.product);
      return true;
    }
    resetProductForm(barcode);
    productLookupMode = "new";
    els.productBarcode.value = payload.data?.barcode || barcode;
    updateProductMode();
    els.productName.focus();
    return true;
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para consultar o produto.");
    productLookupMode = "idle";
    updateProductMode();
    return false;
  } finally {
    els.productLookupButton.disabled = false;
  }
}

async function saveProductChanges() {
  const existing = db.products.find((item) => item.id === els.editingProductId.value);
  if (!existing) return alert("Consulte um produto cadastrado antes de salvar alterações.");
  const product = await productPayloadFromForm(existing);
  if (!product) return;
  try {
    const response = await fetch(`/api/products/${encodeURIComponent(existing.id)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(product),
    });
    const payload = await responsePayload(response);
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      return alert(payload.error || "Não foi possível salvar as alterações.");
    }
    applyProductLocally(payload.data);
    persistLocalOnly();
    populateProductForm(payload.data);
    renderAll();
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para salvar as alterações.");
  }
}

async function confirmProductEntry(event) {
  event.preventDefault();
  if (productLookupMode === "idle" && !(await lookupProductByCode())) return;
  const existing = db.products.find((item) => item.id === els.editingProductId.value);
  const quantity = Number(els.productEntryQuantity.value);
  if (!Number.isInteger(quantity) || quantity <= 0) {
    return alert("A quantidade da entrada deve ser um número inteiro maior que zero.");
  }
  const product = await productPayloadFromForm(existing);
  if (!product) return;
  if (!pendingProductEntryKey) pendingProductEntryKey = createId();
  els.confirmProductEntryButton.disabled = true;
  try {
    const response = await fetch("/api/stock-entries", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Idempotency-Key": pendingProductEntryKey,
      },
      body: JSON.stringify({ product, quantity }),
    });
    const payload = await responsePayload(response);
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      return alert(payload.error || "Não foi possível confirmar a entrada.");
    }
    applyProductLocally(payload.data.product);
    db.stockEntries = [
      payload.data.entry,
      ...(db.stockEntries || []).filter((item) => item.id !== payload.data.entry.id),
    ];
    if (payload.data.movement) {
      db.stockMovements = [
        payload.data.movement,
        ...(db.stockMovements || []).filter((item) => item.id !== payload.data.movement.id),
      ];
    }
    if (payload.data.inventoryMovement) {
      db.inventoryMovements = [
        payload.data.inventoryMovement,
        ...(db.inventoryMovements || []).filter(
          (item) => item.id !== payload.data.inventoryMovement.id,
        ),
      ];
    }
    pendingProductEntryKey = "";
    persistLocalOnly();
    resetProductForm();
    renderAll();
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor. Tente novamente para reutilizar a mesma confirmação.");
  } finally {
    els.confirmProductEntryButton.disabled = false;
  }
}

function applyProductLocally(product) {
  catalogData = { items: [], total: 0, filters: {}, query: {} };
  db.products = db.products.some((item) => item.id === product.id)
    ? db.products.map((item) => item.id === product.id ? product : item)
    : [product, ...db.products];
}

function resetProductForm(value = "") {
  const preservedBarcode = typeof value === "string" ? value : "";
  els.productForm.reset();
  els.editingProductId.value = "";
  els.productBarcode.value = preservedBarcode;
  els.productMinStock.value = "0";
  els.productActive.checked = true;
  els.productCost.value = "0";
  els.productPrice.value = "0";
  els.productMargin.value = "0";
  els.productEntryQuantity.value = "1";
  productPhotoData = "";
  productPhotoFile = null;
  pendingProductEntryKey = "";
  productLookupMode = preservedBarcode ? "new" : "idle";
  setProductStockSummary();
  updateProductMode();
}

function editProduct(id) {
  const product = db.products.find((item) => item.id === id);
  if (!product) return;
  populateProductForm(product);
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
  const id = els.editingCustomerId.value;
  const existing = db.customers.find((customer) => customer.id === id);
  const customer = {
    name: els.customerName.value.trim(),
    cpf: els.customerCpf.value.trim(),
    rg: els.customerRg.value.trim(),
    birth: els.customerBirth.value,
    whatsapp: els.customerWhatsapp.value.trim(),
    email: els.customerEmail.value.trim(),
    address: els.customerAddress.value.trim(),
    addressNumber: els.customerAddressNumber.value.trim(),
    city: els.customerCity.value.trim(),
    district: els.customerDistrict.value.trim(),
    state: els.customerState.value.trim(),
    zip: els.customerZip.value.trim(),
    notes: els.customerNotes.value.trim(),
    limit: readNumber(els.customerLimit.value),
  };

  if (!BACKEND_ENABLED) return showBackendRequiredMessage();
  await submitCustomer(customer, existing);
}

async function submitCustomer(customer, existing, duplicateAcknowledged = false) {
  const id = existing?.id || "";
  try {
    const response = await fetch(existing ? `/api/customers/${encodeURIComponent(id)}` : "/api/customers", {
      method: existing ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...customer, duplicateAcknowledged }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return false;
      if (payload.code === "POSSIBLE_DUPLICATE" && !duplicateAcknowledged) {
        const matches = (payload.warnings || [])
          .map((warning) => `${warning.customerName} (${(warning.fields || []).join(" e ")})`)
          .join("\n");
        const confirmed = confirm(
          `Encontramos possível cadastro duplicado:\n${matches}\n\nDeseja salvar mesmo assim?`
        );
        return confirmed ? submitCustomer(customer, existing, true) : false;
      }
      alert(payload.error || "Não foi possível salvar o cliente.");
      return false;
    }
    applyCustomerLocally(payload.data || customer);
    persistLocalOnly();
    resetCustomerForm();
    renderAll();
    return true;
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para salvar o cliente.");
    return false;
  }
}

function applyCustomerLocally(customer) {
  db.customers = db.customers.some((item) => item.id === customer.id)
    ? db.customers.map((item) => item.id === customer.id ? { ...item, ...customer } : item)
    : [customer, ...db.customers];
}

function resetCustomerForm() {
  els.customerForm.reset();
  els.editingCustomerId.value = "";
  els.customerCode.value = nextCustomerCode();
  els.customerLimit.value = "";
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
  els.customerAddressNumber.value = customer.addressNumber || "";
  els.customerCity.value = customer.city;
  els.customerDistrict.value = customer.district;
  els.customerState.value = customer.state || "";
  els.customerZip.value = customer.zip;
  els.customerNotes.value = customer.notes || "";
  els.customerLimit.value = fixed(customer.limit);
  activateSubtab("cad-cliente");
  els.customerName.focus();
}

async function openCustomerDetails(id) {
  const customer = db.customers.find((item) => item.id === id);
  if (!customer || !BACKEND_ENABLED) return;
  selectedCustomerDetailId = id;
  els.customerDetailTitle.textContent = customer.name;
  els.customerDetailSubtitle.textContent = "Carregando histórico...";
  els.customerDetailContent.innerHTML = '<div class="customer-detail-empty">Carregando dados do cliente...</div>';
  els.customerDetailModal.hidden = false;
  try {
    const [response, scoreResponse] = await Promise.all([
      fetch(`/api/customers/${encodeURIComponent(id)}`, { cache: "no-store" }),
      fetch(`/api/customers/${encodeURIComponent(id)}/score`, { cache: "no-store" }),
    ]);
    const payload = await response.json().catch(() => ({}));
    const scorePayload = await scoreResponse.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return closeCustomerDetail();
      throw new Error(payload.error || "Não foi possível carregar a ficha do cliente.");
    }
    if (scoreResponse.ok && scorePayload.data) {
      customerScoreCache.set(id, scorePayload.data);
      payload.data.score = scorePayload.data;
    }
    renderCustomerDetail(payload.data);
  } catch (error) {
    console.warn(error);
    els.customerDetailContent.innerHTML = `<div class="customer-detail-empty">${escapeHtml(error.message)}</div>`;
  }
}

function closeCustomerDetail() {
  els.customerDetailModal.hidden = true;
  selectedCustomerDetailId = "";
}

function openCustomerStatusModal(customer) {
  els.customerStatusId.value = customer.id;
  els.customerStatusName.textContent = customer.name;
  els.customerStatusValue.value = customer.status === "deactivated" ? "active" : customer.status;
  els.customerStatusReason.value = "";
  els.customerStatusModal.hidden = false;
}

function closeCustomerStatusModal() {
  els.customerStatusModal.hidden = true;
  els.customerStatusForm.reset();
  els.customerStatusId.value = "";
}

async function saveCustomerStatus(event) {
  event.preventDefault();
  const id = els.customerStatusId.value;
  const status = els.customerStatusValue.value;
  const reason = els.customerStatusReason.value.trim();
  if (status === "blocked" && !reason) return alert("Informe o motivo do bloqueio.");
  try {
    const response = await fetch(`/api/customers/${encodeURIComponent(id)}/status`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status, reason }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      return alert(payload.error || "Não foi possível alterar a situação do cliente.");
    }
    applyCustomerLocally(payload.data);
    persistLocalOnly();
    closeCustomerStatusModal();
    closeCustomerDetail();
    renderAll();
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para alterar a situação.");
  }
}

async function saveSupplier(event) {
  event.preventDefault();
  const id = els.editingSupplierId.value || createId();
  const existing = db.suppliers.find((supplier) => supplier.id === id);
  const supplier = {
    id,
    name: els.supplierName.value.trim(),
    tradeName: els.supplierTradeName.value.trim(),
    document: els.supplierCnpj.value.trim(),
    phone: els.supplierPhone.value.trim(),
    whatsapp: els.supplierWhatsapp.value.trim(),
    email: els.supplierEmail.value.trim(),
    zip: els.supplierZip.value.trim(),
    address: els.supplierAddress.value.trim(),
    addressNumber: els.supplierAddressNumber.value.trim(),
    district: els.supplierDistrict.value.trim(),
    city: els.supplierCity.value.trim(),
    state: els.supplierState.value.trim(),
    notes: els.supplierNotes.value.trim(),
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
        if (handleUnauthorized(response, payload)) return;
        alert(payload.error || "Não foi possível salvar o fornecedor.");
        return;
      }
      const savedSupplier = payload.data || supplier;
      applySupplierLocally(savedSupplier);
      persistLocalOnly();
      resetSupplierForm();
      if (returnToPayableAfterSupplier) {
        returnToPayableAfterSupplier = false;
        activateTab("contas");
        els.payableFormPanel.hidden = false;
        els.payableSupplier.value = savedSupplier.name;
        els.payableSupplier.focus();
      } else if (returnToProductAfterSupplier) {
        returnToProductAfterSupplier = false;
        activateSubtab("cad-produto");
        els.productSupplier.value = savedSupplier.name;
        els.productSupplier.focus();
      }
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
  if (returnToPayableAfterSupplier) {
    returnToPayableAfterSupplier = false;
    activateTab("contas");
    els.payableFormPanel.hidden = false;
    els.payableSupplier.value = supplier.name;
  } else if (returnToProductAfterSupplier) {
    returnToProductAfterSupplier = false;
    activateSubtab("cad-produto");
    els.productSupplier.value = supplier.name;
  }
  renderAll();
}

function mergeInventoryMovements(items = []) {
  const incoming = Array.isArray(items) ? items : [];
  const incomingIds = new Set(incoming.map((item) => item.id));
  db.inventoryMovements = [
    ...incoming,
    ...(db.inventoryMovements || []).filter((item) => !incomingIds.has(item.id)),
  ];
}

async function refreshInventoryMovements() {
  if (!BACKEND_ENABLED) return;
  try {
    const response = await fetch("/api/inventory-movements", { cache: "no-store" });
    const payload = await responsePayload(response);
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      return;
    }
    db.inventoryMovements = Array.isArray(payload.data) ? payload.data : [];
  } catch (error) {
    console.warn(error);
  }
}

function openSupplierFromPayable() {
  returnToPayableAfterSupplier = true;
  returnToProductAfterSupplier = false;
  resetSupplierForm();
  activateTab("cadastros");
  activateSubtab("cad-fornecedor");
  els.supplierName.focus();
}

function openSupplierFromProduct() {
  returnToProductAfterSupplier = true;
  returnToPayableAfterSupplier = false;
  resetSupplierForm();
  activateSubtab("cad-fornecedor");
  els.supplierName.focus();
}

function openQuickProductCatalog(collection) {
  const config = catalogFrontendConfig(collection);
  if (!config) return;
  quickProductCatalogContext = collection;
  els[config.editingId].value = "";
  els[config.inputId].value = "";
  activateTab("cadastros");
  activateSubtab(config.panel);
  els[config.inputId].focus();
}

function completeQuickProductCatalog(collection, item) {
  if (quickProductCatalogContext !== collection) return;
  const config = catalogFrontendConfig(collection);
  quickProductCatalogContext = null;
  activateSubtab("cad-produto");
  els[`product${config.field[0].toUpperCase()}${config.field.slice(1)}`].value = item.name;
}

function applySupplierLocally(supplier) {
  db.suppliers = db.suppliers.some((item) => item.id === supplier.id)
    ? db.suppliers.map((item) => item.id === supplier.id ? supplier : item)
    : [supplier, ...db.suppliers];
}

async function saveSimpleName(event, collection, input) {
  event.preventDefault();
  const value = input.value.trim();
  const config = catalogFrontendConfig(collection);
  const editingInput = els[config.editingId];
  const currentId = editingInput.value;
  const duplicate = db[collection].some((item) => normalize(item.name) === normalize(value) && item.id !== currentId);
  if (!value) return;
  if (duplicate) return alert("Nome já cadastrado.");
  if (BACKEND_ENABLED) {
    try {
      const response = await fetch(currentId ? `${config.endpoint}/${encodeURIComponent(currentId)}` : config.endpoint, {
        method: currentId ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: value }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        if (handleUnauthorized(response, payload)) return;
        alert(payload.error || "Não foi possível salvar o cadastro.");
        return;
      }
      const savedItem = payload.data || { id: currentId || createId(), name: value };
      applySimpleNameLocally(collection, savedItem);
      input.value = "";
      editingInput.value = "";
      persistLocalOnly();
      completeQuickProductCatalog(collection, savedItem);
      renderAll();
      return;
    } catch (error) {
      console.warn(error);
      alert("Não foi possível conectar ao servidor para salvar o cadastro.");
      return;
    }
  }
  const savedItem = { id: currentId || createId(), name: value, status: "active" };
  applySimpleNameLocally(collection, savedItem);
  input.value = "";
  editingInput.value = "";
  persist();
  completeQuickProductCatalog(collection, savedItem);
  renderAll();
}

function catalogFrontendConfig(collection) {
  return {
    brands: { endpoint: "/api/brands", editingId: "editingBrandName", inputId: "brandName", panel: "cad-marca", field: "brand", idField: "brandId" },
    categories: { endpoint: "/api/categories", editingId: "editingCategoryName", inputId: "categoryName", panel: "cad-categoria", field: "category", idField: "categoryId" },
    sizes: { endpoint: "/api/sizes", editingId: "editingSizeId", inputId: "sizeName", panel: "cad-tamanho", field: "size", idField: "sizeId" },
    colors: { endpoint: "/api/colors", editingId: "editingColorId", inputId: "colorName", panel: "cad-cor", field: "color", idField: "colorId" },
    expenseCategories: { endpoint: "/api/expense-categories", editingId: "editingExpenseCategoryId", inputId: "expenseCategoryName", panel: "cad-despesa" },
  }[collection];
}

function applySimpleNameLocally(collection, item) {
  const normalizedItem = { ...item, name: catalogName(item), status: item.status || "active" };
  db[collection] = db[collection].some((value) => value.id === normalizedItem.id)
    ? db[collection].map((value) => value.id === normalizedItem.id ? normalizedItem : value)
    : [...db[collection], normalizedItem];
  const config = catalogFrontendConfig(collection);
  if (config?.field) {
    db.products = db.products.map((product) => product[config.idField] === normalizedItem.id
      ? { ...product, [config.field]: normalizedItem.name }
      : product);
  }
}

async function saveUser(event) {
  event.preventDefault();
  if (!BACKEND_ENABLED) return showBackendRequiredMessage();
  if (!isAdmin()) return alert("Apenas admin pode criar usuários.");
  const id = els.editingUserId.value || createId();
  const existing = db.users.find((user) => user.id === id);
  const duplicate = db.users.some((user) => user.login === els.userLogin.value.trim() && user.id !== id);
  if (duplicate) return alert("Usuário já cadastrado.");
  const password = els.userPassword.value;
  const user = {
    id,
    name: els.userName.value.trim(),
    login: els.userLogin.value.trim(),
    role: els.userRole.value,
    active: existing?.active ?? true,
  };
  if (!existing && !password) return alert("Senha é obrigatória para novo usuário.");

  try {
    const response = await fetch(existing ? `/api/users/${encodeURIComponent(id)}` : "/api/users", {
      method: existing ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...user, ...(password ? { password } : {}) }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      alert(payload.error || "Não foi possível salvar o usuário.");
      return;
    }
    applyUserLocally(payload.data || user);
    persistLocalOnly();
    resetUserForm();
    renderAll();
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para salvar o usuário.");
  }
}

function applyUserLocally(user) {
  const publicUser = sanitizeUserForBrowser(user);
  db.users = db.users.some((item) => item.id === user.id)
    ? db.users.map((item) => item.id === publicUser.id ? publicUser : item)
    : [...db.users, publicUser];
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
  els.supplierTradeName.value = supplier.tradeName || "";
  els.supplierCnpj.value = supplier.document || supplier.cnpj || "";
  els.supplierPhone.value = supplier.phone || "";
  els.supplierWhatsapp.value = supplier.whatsapp || "";
  els.supplierEmail.value = supplier.email || "";
  els.supplierZip.value = supplier.zip || "";
  els.supplierAddress.value = supplier.address || "";
  els.supplierAddressNumber.value = supplier.addressNumber || "";
  els.supplierDistrict.value = supplier.district || "";
  els.supplierCity.value = supplier.city || "";
  els.supplierState.value = supplier.state || "";
  els.supplierNotes.value = supplier.notes || "";
  activateSubtab("cad-fornecedor");
}

async function deleteSupplier(id) {
  const supplier = db.suppliers.find((item) => item.id === id);
  if (!supplier) return;
  const newStatus = supplier.status === "deactivated" ? "active" : "deactivated";
  if (!confirm(`${newStatus === "active" ? "Reativar" : "Desativar"} fornecedor ${supplier.name}?`)) return;
  await changeSupplierStatus(supplier, newStatus);
}

async function changeSupplierStatus(supplier, status, confirmed = false) {
  try {
    const response = await fetch(`/api/suppliers/${encodeURIComponent(supplier.id)}/status`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status, confirmed, reason: status === "deactivated" ? "Desativação pelo cadastro" : "Reativação pelo cadastro" }),
    });
    const payload = await response.json().catch(() => ({}));
    if (response.status === 409 && payload.code === "confirmation_required" && !confirmed) {
      const summary = payload.summary || {};
      if (confirm(`Este fornecedor possui ${money.format(summary.openAmount || 0)} em aberto. Confirmar desativação?`)) {
        return changeSupplierStatus(supplier, status, true);
      }
      return;
    }
    if (!response.ok) return alert(payload.error || "Não foi possível alterar o fornecedor.");
    applySupplierLocally(payload.data);
    persistLocalOnly();
    renderAll();
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para alterar o fornecedor.");
  }
}

async function openSupplierDetail(id) {
  try {
    const response = await fetch(`/api/suppliers/${encodeURIComponent(id)}`, { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) return alert(payload.error || "Não foi possível carregar o fornecedor.");
    const {
      supplier, payables = [], statusHistory = [],
      entries = [], returns = [], credits = [],
    } = payload.data;
    els.supplierDetailTitle.textContent = supplier.name;
    els.supplierDetailContent.innerHTML = `
      <div class="supplier-detail-summary">
        <p><strong>Documento</strong><span>${escapeHtml(supplier.document || "-")}</span></p>
        <p><strong>Contato</strong><span>${escapeHtml(supplier.whatsapp || supplier.phone || "-")}</span></p>
        <p><strong>Saldo em aberto</strong><span>${money.format(supplier.openAmount || 0)}</span></p>
        <p><strong>Saldo vencido</strong><span>${money.format(supplier.overdueAmount || 0)}</span></p>
        <p><strong>Crédito disponível</strong><span>${money.format(supplier.creditAvailable || 0)}</span></p>
      </div>
      <section class="customer-detail-section"><h3>Entradas</h3>
        ${entries.length ? entries.map((item) => `<p><strong>${escapeHtml(item.code || item.id)}</strong> · ${money.format(item.totalCost || 0)} · ${escapeHtml(formatDateTime(item.createdAt))}</p>`).join("") : '<p class="customer-detail-empty">Nenhuma Entrada vinculada.</p>'}
      </section>
      <section class="customer-detail-section"><h3>Devoluções e créditos</h3>
        ${returns.length ? returns.map((item) => `<p><strong>${escapeHtml(item.code || item.id)}</strong> · ${money.format(item.totalValue || 0)} · ${escapeHtml(item.financialStatus || "pending")}</p>`).join("") : '<p class="customer-detail-empty">Nenhuma devolução.</p>'}
        ${credits.length ? credits.map((item) => `<p>Crédito ${escapeHtml(item.status)} · disponível ${money.format(item.availableAmount || 0)}</p>`).join("") : ""}
      </section>
      <section class="customer-detail-section"><h3>Contas vinculadas</h3>
        ${payables.length ? payables.map((item) => `<p><strong>${escapeHtml(item.category || "-")}</strong> · ${money.format(item.amount || 0)} · ${escapeHtml(formatDate(item.dueDate))}</p>`).join("") : '<p class="customer-detail-empty">Nenhuma conta vinculada.</p>'}
      </section>
      <section class="customer-detail-section"><h3>Histórico de situação</h3>
        ${statusHistory.length ? statusHistory.map((item) => `<p>${escapeHtml(item.previousStatus)} → ${escapeHtml(item.newStatus)} · ${escapeHtml(formatDateTime(item.createdAt))}</p>`).join("") : '<p class="customer-detail-empty">Sem alterações.</p>'}
      </section>`;
    const returnSection = els.supplierDetailContent.querySelectorAll(".customer-detail-section")[1];
    returns
      .filter((item) => item.status === "confirmed")
      .forEach((item) => {
        returnSection?.append(button(
          `Cancelar ${item.code || "devolucao"}`,
          "ghost small danger-text",
          () => cancelSupplierReturn(item.id, supplier.id),
        ));
      });
    els.supplierDetailModal.hidden = false;
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor.");
  }
}

async function cancelSupplierReturn(returnId, supplierId) {
  if (!confirm("Cancelar esta devolucao e recompor o estoque?")) return;
  try {
    const response = await fetch(`/api/supplier-returns/${encodeURIComponent(returnId)}/cancel`, {
      method: "POST",
    });
    const payload = await responsePayload(response);
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      return alert(payload.error || "Nao foi possivel cancelar a devolucao.");
    }
    (payload.data.products || []).forEach(applyProductLocally);
    db.supplierReturns = db.supplierReturns.map((item) => (
      item.id === returnId ? { ...item, status: "cancelled" } : item
    ));
    db.stockMovements = [...(payload.data.movements || []), ...db.stockMovements];
    await syncFromServer();
    persistLocalOnly();
    renderAll();
    await openSupplierDetail(supplierId);
  } catch (error) {
    console.warn(error);
    alert("Nao foi possivel conectar ao servidor.");
  }
}

function closeSupplierDetail() {
  els.supplierDetailModal.hidden = true;
  els.supplierDetailContent.innerHTML = "";
}

function editSimpleName(collection, id) {
  const config = catalogFrontendConfig(collection);
  const item = db[collection].find((value) => value.id === id);
  if (!config || !item) return;
  els[config.editingId].value = item.id;
  els[config.inputId].value = item.name;
  activateSubtab(config.panel);
  els[config.inputId].focus();
}

async function deleteSimpleName(collection, id) {
  const config = catalogFrontendConfig(collection);
  const item = db[collection].find((value) => value.id === id);
  if (!item || !config) return;
  const newStatus = item.status === "deactivated" ? "active" : "deactivated";
  if (!confirm(`${newStatus === "active" ? "Reativar" : "Desativar"} ${item.name}?`)) return;
  if (BACKEND_ENABLED) {
    try {
      const response = await fetch(`${config.endpoint}/${encodeURIComponent(item.id)}/status`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        alert(payload.error || "Não foi possível alterar o cadastro.");
        return;
      }
      applySimpleNameLocally(collection, payload.data);
      persistLocalOnly();
      renderAll();
      return;
    } catch (error) {
      console.warn(error);
      alert("Não foi possível conectar ao servidor para alterar o cadastro.");
      return;
    }
  }
  applySimpleNameLocally(collection, { ...item, status: newStatus });
  persist();
  renderAll();
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

async function deleteUser(id) {
  if (!isAdmin()) return alert("Apenas admin pode desativar usuários.");
  const user = db.users.find((item) => item.id === id);
  if (!user || !confirm(`Desativar usuário ${user.name}?`)) return;
  if (BACKEND_ENABLED) {
    try {
      const response = await fetch(`/api/users/${encodeURIComponent(id)}`, { method: "DELETE" });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        alert(payload.error || "Não foi possível desativar o usuário.");
        return;
      }
      db.users = db.users.map((item) => item.id === id ? { ...item, active: false } : item);
      persistLocalOnly();
      renderAll();
      return;
    } catch (error) {
      console.warn(error);
      alert("Não foi possível conectar ao servidor para desativar o usuário.");
      return;
    }
  }
  if (session?.user?.id === id) return alert("Não é possível excluir o usuário logado.");
  const activeAdmins = db.users.filter((item) => item.role === "admin" && item.active !== false);
  if (user.role === "admin" && activeAdmins.length <= 1) return alert("Não é possível excluir o último administrador.");
  db.users = db.users.filter((item) => item.id !== id);
  persist();
  renderAll();
}

async function unlockUser(id) {
  if (!isAdmin()) return;
  try {
    const response = await fetch(`/api/users/${encodeURIComponent(id)}/unlock`, { method: "POST" });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      return alert(payload.error || "Não foi possível desbloquear o usuário.");
    }
    db.users = db.users.map((item) => item.id === id ? { ...item, blocked: false } : item);
    persistLocalOnly();
    renderUsers();
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para desbloquear o usuário.");
  }
}

function renderAll() {
  [
    applySession,
    renderOptions,
    renderCadastroCards,
    renderProducts,
    renderProductEntryHistory,
    renderCustomers,
    renderSuppliers,
    renderSimpleLists,
    renderUsers,
    renderDashboard,
    renderCatalog,
    renderStock,
    renderPhysicalInventories,
    renderSaleProducts,
    renderCart,
    renderConditionalPanels,
    renderConditionalProducts,
    renderConditionalCart,
    renderConditionalOpenList,
    renderConditionalFinalizePanel,
    renderSaleHistory,
    renderManualReceiptSummary,
    renderAfterSalesSelection,
    renderExchangeItems,
    renderAfterSalesHistory,
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
  const customers = db.customers.filter((customer) => !customer.isDefault);
  els.customerCardCount.textContent = `${customers.length} cliente${customers.length === 1 ? "" : "s"} cadastrado${customers.length === 1 ? "" : "s"}`;
  els.supplierCardCount.textContent = `${db.suppliers.length} fornecedor${db.suppliers.length === 1 ? "" : "es"}`;
  els.brandCardCount.textContent = `${db.brands.length} marca${db.brands.length === 1 ? "" : "s"} cadastrada${db.brands.length === 1 ? "" : "s"}`;
  els.categoryCardCount.textContent = `${db.categories.length} categoria${db.categories.length === 1 ? "" : "s"} cadastrada${db.categories.length === 1 ? "" : "s"}`;
  els.sizeCardCount.textContent = `${db.sizes.length} tamanho${db.sizes.length === 1 ? "" : "s"} cadastrado${db.sizes.length === 1 ? "" : "s"}`;
  els.colorCardCount.textContent = `${db.colors.length} cor${db.colors.length === 1 ? "" : "es"} cadastrada${db.colors.length === 1 ? "" : "s"}`;
  els.expenseCategoryCardCount.textContent = `${db.expenseCategories.length} categoria${db.expenseCategories.length === 1 ? "" : "s"} cadastrada${db.expenseCategories.length === 1 ? "" : "s"}`;
  els.cardModalityCardCount.textContent = `${cardModalities.length} modalidade${cardModalities.length === 1 ? "" : "s"}`;
  els.userCardCount.textContent = `${db.users.length} usuário${db.users.length === 1 ? "" : "s"} cadastrado${db.users.length === 1 ? "" : "s"}`;
}

function toDateTimeLocalValue(value) {
  if (!value) return "";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "";
  const year = parsed.getFullYear();
  const month = String(parsed.getMonth() + 1).padStart(2, "0");
  const day = String(parsed.getDate()).padStart(2, "0");
  const hour = String(parsed.getHours()).padStart(2, "0");
  const minute = String(parsed.getMinutes()).padStart(2, "0");
  return `${year}-${month}-${day}T${hour}:${minute}`;
}

function setCardModalityError(message) {
  els.cardModalityFormError.textContent = message || "";
  els.cardModalityFormError.hidden = !message;
}

function updateCardModalityInstallments() {
  const debit = els.cardModalityType.value === "debit";
  els.cardModalityInstallments.disabled = debit;
  if (debit) {
    els.cardModalityInstallments.value = "1";
    return;
  }
  const installments = Math.max(1, Math.min(10, parseInt(els.cardModalityInstallments.value, 10) || 1));
  els.cardModalityInstallments.value = String(installments);
}

async function loadCardModalities(force = false) {
  if (!BACKEND_ENABLED || !isAdmin()) return;
  if (cardModalitiesLoaded && !force) {
    renderCardModalities();
    return;
  }
  els.cardModalityList.innerHTML = `<tr><td colspan="7" class="empty-cell">Carregando modalidades...</td></tr>`;
  try {
    const response = await fetch("/api/card-modalities", { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      throw new Error(payload.error || "Não foi possível carregar modalidades.");
    }
    cardModalities = Array.isArray(payload.data) ? payload.data : [];
    cardModalitiesLoaded = true;
    renderCardModalities();
    renderCadastroCards();
  } catch (error) {
    console.warn(error);
    els.cardModalityList.innerHTML = `<tr><td colspan="7" class="empty-cell">Não foi possível carregar modalidades de cartão.</td></tr>`;
  }
}

async function loadSaleCardModalities(force = false) {
  if (!BACKEND_ENABLED || !session || (saleCardModalitiesLoaded && !force)) return;
  try {
    const response = await fetch("/api/sales/card-modalities", { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      throw new Error(payload.error || "Não foi possível carregar as modalidades de cartão.");
    }
    saleCardModalities = Array.isArray(payload.data) ? payload.data : [];
    saleCardModalitiesLoaded = true;
    refreshSalePaymentMethods();
  } catch (error) {
    console.warn(error);
    saleCardModalities = [];
    saleCardModalitiesLoaded = false;
  }
}

function refreshSalePaymentMethods() {
  els.paymentRows.querySelectorAll(".payment-row").forEach((row) => {
    const select = row.querySelector(".pay-method");
    const current = select.value;
    select.innerHTML = salePaymentOptionsMarkup();
    if ([...select.options].some((option) => option.value === current)) {
      select.value = current;
    } else {
      select.value = "cash";
    }
    updateSalePaymentRow(row);
  });
}

function salePaymentOptionsMarkup() {
  const enabled = storeOperationalSettings.paymentMethods || {};
  const cards = saleCardModalities.filter((modality) => enabled[modality.method]).map((modality) => {
    const label = modality.method === "debit"
      ? `Débito - ${modality.name}`
      : `Crédito ${modality.installments}x - ${modality.name}`;
    return `<option value="card:${escapeHtml(modality.cardModalityId)}">${escapeHtml(label)}</option>`;
  }).join("");
  let markup = `
    <option value="cash">Dinheiro</option>
    ${enabled.pix ? '<option value="pix">PIX</option>' : ""}
    ${cards}
    <option value="storeCredit">Crediário</option>
  `;
  if (!enabled.storeCredit) {
    markup = markup.replace(/<option value="storeCredit">[^<]*<\/option>/, "");
  }
  return markup;
}

function formatCardModalityValidity(modality) {
  if (!modality?.validFrom) return "-";
  const start = formatDateTime(modality.validFrom);
  return modality.validUntil ? `${start} até ${formatDateTime(modality.validUntil)}` : `A partir de ${start}`;
}

function renderCardModalities() {
  const query = normalize(els.cardModalitySearch.value);
  const filtered = cardModalities.filter((item) => (
    !query || normalize(`${item.name} ${item.method} ${item.status}`).includes(query)
  ));
  els.cardModalityList.innerHTML = "";
  if (!filtered.length) {
    els.cardModalityList.innerHTML = `<tr><td colspan="7" class="empty-cell">Nenhuma modalidade encontrada.</td></tr>`;
    return;
  }
  filtered.forEach((modality) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td><strong>${escapeHtml(modality.name)}</strong></td>
      <td>${modality.installments}</td>
      <td>${fixed(modality.taxPercent)}%</td>
      <td>${modality.receivableDays} dia${modality.receivableDays === 1 ? "" : "s"}</td>
      <td>${formatCardModalityValidity(modality)}</td>
      <td><span class="status-pill ${modality.status === "active" ? "" : "off"}">${modality.status === "active" ? "Ativa" : "Inativa"}</span></td>
      <td><div class="table-actions"></div></td>
    `;
    const actions = row.querySelector(".table-actions");
    actions.append(button("Editar", "icon-button", () => editCardModality(modality.cardModalityId)));
    actions.append(button(
      modality.status === "active" ? "Inativar" : "Ativar",
      "icon-button",
      () => toggleCardModalityStatus(
        modality.cardModalityId,
        modality.status === "active" ? "deactivate" : "activate",
      ),
    ));
    actions.append(button("Histórico", "icon-button", () => showCardModalityHistory(modality.cardModalityId)));
    els.cardModalityList.append(row);
  });
}

function resetCardModalityForm() {
  els.cardModalityForm.reset();
  els.editingCardModalityId.value = "";
  els.cardModalityInstallments.value = "1";
  els.cardModalityTaxPercent.value = "0";
  els.cardModalityReceivableDays.value = "1";
  els.cardModalityValidFrom.value = toDateTimeLocalValue(new Date().toISOString());
  els.cardModalityValidUntil.value = "";
  els.cardModalityStatus.checked = true;
  selectedCardModalityId = "";
  els.cardModalityHistoryPanel.hidden = true;
  updateCardModalityInstallments();
  setCardModalityError("");
}

async function saveCardModality(event) {
  event.preventDefault();
  if (!isAdmin()) return;
  setCardModalityError("");
  const cardModalityId = els.editingCardModalityId.value.trim();
  const payload = {
    method: els.cardModalityType.value,
    installments: parseInt(els.cardModalityInstallments.value, 10) || 1,
    taxPercent: readNumber(els.cardModalityTaxPercent.value),
    receivableDays: parseInt(els.cardModalityReceivableDays.value, 10) || 0,
    validFrom: els.cardModalityValidFrom.value || undefined,
    validUntil: els.cardModalityValidUntil.value || "",
    status: els.cardModalityStatus.checked ? "active" : "inactive",
  };
  try {
    const response = await fetch(
      cardModalityId ? `/api/card-modalities/${encodeURIComponent(cardModalityId)}` : "/api/card-modalities",
      {
        method: cardModalityId ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
    );
    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, result)) return;
      setCardModalityError(result.error || "Não foi possível salvar a modalidade.");
      return;
    }
    cardModalitiesLoaded = false;
    await loadCardModalities(true);
    resetCardModalityForm();
  } catch (error) {
    console.warn(error);
    setCardModalityError("Não foi possível conectar ao servidor.");
  }
}

async function toggleCardModalityStatus(cardModalityId, action) {
  try {
    const response = await fetch(`/api/card-modalities/${encodeURIComponent(cardModalityId)}/${action}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      alert(payload.error || "Não foi possível alterar a modalidade.");
      return;
    }
    cardModalitiesLoaded = false;
    await loadCardModalities(true);
    if (selectedCardModalityId === cardModalityId) await showCardModalityHistory(cardModalityId);
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor.");
  }
}

async function showCardModalityHistory(cardModalityId) {
  try {
    const response = await fetch(`/api/card-modalities/${encodeURIComponent(cardModalityId)}/history`, { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      alert(payload.error || "Não foi possível carregar o histórico.");
      return;
    }
    cardModalityHistory = Array.isArray(payload.data) ? payload.data : [];
    selectedCardModalityId = cardModalityId;
    renderCardModalityHistory();
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor.");
  }
}

function renderCardModalityHistory() {
  els.cardModalityHistoryPanel.hidden = false;
  els.cardModalityHistoryList.innerHTML = "";
  cardModalityHistory.forEach((modality) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${escapeHtml(modality.name)}</td>
      <td>${fixed(modality.taxPercent)}%</td>
      <td>${modality.receivableDays} dia${modality.receivableDays === 1 ? "" : "s"}</td>
      <td>${formatDateTime(modality.validFrom)}</td>
      <td>${formatDateTime(modality.validUntil)}</td>
      <td><span class="status-pill ${modality.status === "active" ? "" : "off"}">${modality.status === "active" ? "Ativa" : "Inativa"}</span></td>
    `;
    els.cardModalityHistoryList.append(row);
  });
}

function editCardModality(cardModalityId) {
  const modality = cardModalities.find((item) => item.cardModalityId === cardModalityId);
  if (!modality) return;
  els.editingCardModalityId.value = modality.cardModalityId;
  els.cardModalityType.value = modality.method;
  els.cardModalityInstallments.value = modality.installments;
  els.cardModalityTaxPercent.value = fixed(modality.taxPercent);
  els.cardModalityReceivableDays.value = modality.receivableDays;
  els.cardModalityValidFrom.value = toDateTimeLocalValue(modality.validFrom);
  els.cardModalityValidUntil.value = toDateTimeLocalValue(modality.validUntil);
  els.cardModalityStatus.checked = modality.status === "active";
  updateCardModalityInstallments();
  setCardModalityError("");
}

function renderOptions() {
  populateCashExpenseFilter();
  fillDatalist(els.brandOptions, activeCatalogItems("brands").map(catalogName));
  fillDatalist(els.categoryOptions, activeCatalogItems("categories").map(catalogName));
  fillDatalist(els.sizeOptions, activeCatalogItems("sizes").map(catalogName));
  fillDatalist(els.colorOptions, activeCatalogItems("colors").map(catalogName));
  fillDatalist(els.expenseCategoryOptions, activeCatalogItems("expenseCategories").map(catalogName));
  fillDatalist(
    els.customerOptions,
    db.customers
      .filter((customer) => !customer.isDefault && customer.status !== "deactivated")
      .map((customer) => customer.name)
  );
  fillDatalist(els.productOptions, db.products.map((product) => `${product.barcode} - ${product.name}`));
  fillDatalist(els.saleOptions, db.sales.map((sale) => sale.id));
  fillDatalist(els.supplierOptions, db.suppliers.filter((supplier) => supplier.status !== "deactivated").map((supplier) => supplier.name));
  fillSelect(els.catalogCategoryFilter, activeCatalogItems("categories").map(catalogName), "Todas");
  fillSelect(els.catalogBrandFilter, activeCatalogItems("brands").map(catalogName), "Todas");
  fillSelect(els.catalogSizeFilter, activeCatalogItems("sizes").map(catalogName), "Todos");
  fillSelect(els.catalogColorFilter, activeCatalogItems("colors").map(catalogName), "Todas");
  fillSelect(els.stockCategoryFilter, activeCatalogItems("categories").map(catalogName), "Todas");
  fillSelect(els.stockBrandFilter, activeCatalogItems("brands").map(catalogName), "Todas");
  fillSelect(els.payableCategoryFilter, activeCatalogItems("expenseCategories").map(catalogName), "Todas");
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
    const realStock = Math.max(0, Number(product.stock || 0));
    const reservedStock = Math.max(0, Number(product.reservedStock || openConditionalReservedQty(product.id)));
    const availableStock = Math.max(0, Number(product.availableStock ?? realStock - reservedStock));
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
      <td class="${availableStock <= (product.minStock || 0) ? "danger-text" : ""}">
        <div class="product-stock-cell">
          <strong>${realStock}</strong>
          <small>${availableStock} disp.${reservedStock ? ` | ${reservedStock} reserv.` : ""}</small>
        </div>
      </td>
      <td><span class="status-pill ${product.active === false ? "off" : ""}">${product.active === false ? "Inativo" : "Ativo"}</span></td>
      <td><div class="table-actions"></div></td>
    `;
    const actions = row.querySelector(".table-actions");
    actions.append(button("Editar", "icon-button", () => editProduct(product.id)));
    actions.append(button("Etiqueta", "icon-button", () => printProductLabel(product.id)));
    actions.append(button("Excluir", "icon-button danger-icon", () => deleteProduct(product.id)));
    els.productList.append(row);
  });
}

function renderProductEntryHistory(productId = els.editingProductId?.value || "") {
  if (!els.productEntryHistory || !els.productEntryHistoryCaption) return;
  const entries = (db.stockEntries || [])
    .filter((entry) => !productId || (entry.items || []).some((item) => item.productId === productId))
    .sort((a, b) => String(b.createdAt || "").localeCompare(String(a.createdAt || "")))
    .slice(0, 6);
  const selectedProduct = db.products.find((product) => product.id === productId);
  els.productEntryHistoryCaption.textContent = selectedProduct
    ? `Entradas de ${selectedProduct.name}`
    : "Últimas entradas confirmadas";
  els.productEntryHistory.innerHTML = "";
  if (!entries.length) {
    els.productEntryHistory.innerHTML = '<p class="product-entry-empty">Nenhuma entrada confirmada.</p>';
    return;
  }
  entries.forEach((entry) => {
    const entryItem = (entry.items || [])[0] || {};
    const item = document.createElement("article");
    item.className = "product-entry-row";
    item.innerHTML = `
      <div>
        <strong>${escapeHtml(entry.code || entry.entryNumber || entry.id || "-")}</strong>
        <small>${escapeHtml(entryItem.productName || "-")} | ${escapeHtml(entryItem.barcode || "-")}</small>
      </div>
      <div>
        <span>${Number(entry.totalQuantity || entryItem.quantity || 0)} peça(s)</span>
        <small>${escapeHtml(entry.supplier || "Fornecedor não informado")} | ${money.format(entryItem.unitCost || 0)} un.</small>
      </div>
      <div>
        <strong>${money.format(entry.totalCost || 0)}</strong>
        <small>${escapeHtml(entry.status === "confirmed" ? "Confirmada" : entry.status === "cancelled" ? "Cancelada" : entry.status || "-")} | ${escapeHtml(formatDateTime(entry.createdAt))} | ${escapeHtml(entry.userName || "-")}</small>
      </div>
      <div class="product-entry-actions"></div>
    `;
    const actions = item.querySelector(".product-entry-actions");
    if (entry.status === "confirmed") {
      actions.append(button("Conta a pagar", "ghost small", () => createPayableFromEntry(entry)));
      actions.append(button("Devolver", "ghost small", () => createSupplierReturnFromEntry(entry)));
      actions.append(button("Cancelar", "ghost small danger-text", () => cancelPurchaseEntry(entry)));
    }
    els.productEntryHistory.append(item);
  });
}

async function createPayableFromEntry(entry) {
  const amountText = prompt("Valor da conta a pagar:", fixed(entry.totalCost || 0));
  if (amountText === null) return;
  const amount = Number(String(amountText).replace(",", "."));
  if (!(amount > 0)) return alert("Informe um valor válido.");
  const dueDate = prompt("Data de vencimento (AAAA-MM-DD):", todayIso);
  if (!dueDate) return;
  try {
    const response = await fetch(`/api/stock-entries/${encodeURIComponent(entry.id)}/payables`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount, dueDate, notes: `Entrada ${entry.code || entry.id}` }),
    });
    const payload = await responsePayload(response);
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      return alert(payload.error || "Não foi possível gerar a conta.");
    }
    payload.data.payables.forEach(applyPayableLocally);
    db.stockEntries = db.stockEntries.map((item) => item.id === entry.id ? payload.data.entry : item);
    persistLocalOnly();
    renderAll();
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor.");
  }
}

async function cancelPurchaseEntry(entry) {
  const reason = prompt("Motivo obrigatório do cancelamento da Entrada:");
  if (!reason?.trim()) return;
  if (!confirm("O estoque recebido será retirado e contas pendentes vinculadas serão canceladas. Continuar?")) return;
  try {
    const response = await fetch(`/api/stock-entries/${encodeURIComponent(entry.id)}/cancel`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Idempotency-Key": createId() },
      body: JSON.stringify({ reason: reason.trim() }),
    });
    const payload = await responsePayload(response);
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      return alert(payload.error || "Não foi possível cancelar a Entrada.");
    }
    (payload.data.products || []).forEach(applyProductLocally);
    const cancelled = new Set(payload.data.cancelledPayableIds || []);
    db.payables = db.payables.map((item) => cancelled.has(item.id) ? { ...item, status: "cancelled" } : item);
    db.stockEntries = db.stockEntries.map((item) => item.id === entry.id ? payload.data.entry : item);
    db.stockMovements = [...(payload.data.movements || []), ...db.stockMovements];
    mergeInventoryMovements(payload.data.inventoryMovements || []);
    persistLocalOnly();
    renderAll();
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor.");
  }
}

async function createSupplierReturnFromEntry(entry) {
  const source = (entry.items || [])[0];
  if (!source) return alert("A Entrada não possui itens disponíveis.");
  const quantityText = prompt(`Quantidade de ${source.productName || "produto"} a devolver:`, "1");
  if (quantityText === null) return;
  const quantity = Number(quantityText);
  if (!Number.isInteger(quantity) || quantity <= 0) return alert("Informe uma quantidade inteira válida.");
  const reason = prompt("Motivo obrigatório da devolução ao fornecedor:");
  if (!reason?.trim()) return;
  const treatment = prompt("Tratamento financeiro: pendente, conta, credito, dinheiro ou pix", "pendente");
  if (treatment === null) return;
  const total = round(quantity * Number(source.unitCost || 0));
  const financial = {};
  const normalizedTreatment = normalize(treatment);
  if (!["pendente", "conta", "credito", "dinheiro", "pix"].includes(normalizedTreatment)) {
    return alert("Escolha pendente, conta, credito, dinheiro ou pix.");
  }
  if (normalizedTreatment === "conta") {
    const candidates = (entry.payables || []).filter((item) => {
      const open = Number(item.openAmount ?? payableBalance(item));
      return item.status !== "cancelled" && open > 0.01;
    });
    if (!candidates.length) return alert("A Entrada nao possui conta vinculada com saldo em aberto.");
    const options = candidates
      .map((item, index) => `${index + 1} - ${formatDate(item.dueDate)} - ${money.format(item.openAmount ?? payableBalance(item))}`)
      .join("\n");
    const selectedText = prompt(`Escolha a conta para abatimento:\n${options}`, "1");
    if (selectedText === null) return;
    const selected = candidates[Number(selectedText) - 1];
    if (!selected) return alert("Selecione uma conta valida.");
    const available = Number(selected.openAmount ?? payableBalance(selected));
    if (total - available > 0.01) {
      return alert("O valor da devolucao excede o saldo da conta escolhida. Use outro tratamento financeiro.");
    }
    financial.payableAbatements = [{ payableId: selected.id, amount: total }];
  }
  if (normalizedTreatment === "credito") financial.creditAmount = total;
  if (normalizedTreatment === "dinheiro") financial.cashRefund = total;
  if (normalizedTreatment === "pix") financial.pixRefund = total;
  try {
    const response = await fetch("/api/supplier-returns", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Idempotency-Key": createId() },
      body: JSON.stringify({
        entryId: entry.id,
        reason: reason.trim(),
        items: [{ entryItemId: source.id, quantity }],
        financial,
      }),
    });
    const payload = await responsePayload(response);
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      return alert(payload.error || "Não foi possível registrar a devolução.");
    }
    (payload.data.products || []).forEach(applyProductLocally);
    db.supplierReturns = [payload.data.return, ...db.supplierReturns.filter((item) => item.id !== payload.data.return.id)];
    db.stockMovements = [...(payload.data.movements || []), ...db.stockMovements];
    db.cash = [...(payload.data.cash || []), ...db.cash];
    await syncFromServer();
    persistLocalOnly();
    renderAll();
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor.");
  }
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
  const rows = db.customers.filter((customer) => !customer.isDefault).map((customer) => {
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
      numero: customer.addressNumber,
      cidade: customer.city,
      bairro: customer.district,
      estado: customer.state,
      cep: customer.zip,
      observacoes: customer.notes,
      limite_credito: fixed(customer.limit),
      saldo_aberto: fixed(stats.open),
      situacao: customerStatusLabel(customer.status),
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
  const filter = els.customerStatusFilter.value;
  const baseCustomers = db.customers.filter((customer) => !customer.isDefault);
  const customers = baseCustomers.filter((customer) => {
    const matchesQuery = !query
      || normalize(customer.name).includes(query)
      || normalize(customer.cpf).includes(query)
      || normalize(customer.whatsapp).includes(query);
    const matchesStatus = filter === "all"
      || (filter === "operational" && customer.status !== "deactivated")
      || customer.status === filter;
    return matchesQuery && matchesStatus;
  });
  const operational = baseCustomers.filter((customer) => customer.status !== "deactivated");
  const withOpen = operational.filter((customer) => Number(customer.openCredit ?? customerDebt(customer.id).open) > 0);
  const withOverdue = operational.filter((customer) => Number(customer.overdueCredit || 0) > 0);
  els.customerTotalKpi.textContent = String(operational.filter((customer) => customer.status === "active").length);
  els.customerOpenKpi.textContent = String(withOpen.length);
  els.customerOverdueKpi.textContent = String(withOverdue.length);
  els.customerReceivableKpi.textContent = money.format(
    operational.reduce((total, customer) => total + Number(customer.openCredit ?? customerDebt(customer.id).open), 0)
  );
  els.customerList.innerHTML = "";
  if (!customers.length) {
    els.customerList.innerHTML = `<tr><td colspan="7" class="empty-cell">Nenhum cliente encontrado.</td></tr>`;
    return;
  }
  customers.forEach((customer) => {
    const open = Number(customer.openCredit ?? customerDebt(customer.id).open);
    const row = document.createElement("tr");
    row.innerHTML = `
      <td><div class="customer-cell"><strong>${escapeHtml(customer.name)}</strong><small>${escapeHtml(customer.code || "-")}</small></div></td>
      <td>${escapeHtml(customer.cpf || "-")}</td>
      <td>${escapeHtml(customer.whatsapp || "-")}</td>
      <td>${money.format(customer.limit || 0)}</td>
      <td class="${open > 0 ? "danger-text" : ""}">${money.format(open)}</td>
      <td><span class="customer-status ${escapeHtml(customer.status || "active")}">${escapeHtml(customerStatusLabel(customer.status))}</span></td>
      <td><div class="table-actions"></div></td>
    `;
    const actions = row.querySelector(".table-actions");
    actions.append(button("Ver", "icon-button", () => openCustomerDetails(customer.id)));
    actions.append(button("Editar", "icon-button", () => editCustomer(customer.id)));
    els.customerList.append(row);
  });
}

function customerStatusLabel(status) {
  return { active: "Ativo", blocked: "Bloqueado", deactivated: "Desativado" }[status] || "Ativo";
}

function renderCustomerDetail(data = {}) {
  const customer = data.customer || {};
  const summary = data.summary || {};
  selectedCustomerDetailId = customer.id || selectedCustomerDetailId;
  els.customerDetailTitle.textContent = customer.name || "Ficha do cliente";
  els.customerDetailSubtitle.textContent = `${customer.code || "-"} · ${customerStatusLabel(customer.status)}`;
  els.customerDetailStatusButton.textContent = customer.status === "deactivated"
    ? "Reativar cliente"
    : "Alterar situação";
  const sales = data.sales || [];
  const receivables = data.receivables || [];
  const conditionals = data.conditionals || [];
  const statusHistory = data.statusHistory || [];
  const limitHistory = data.creditLimitHistory || [];
  const score = data.score || customerScoreCache.get(customer.id);
  els.customerDetailContent.innerHTML = `
    <div class="customer-detail-kpis">
      <article><span>Total comprado</span><strong>${money.format(summary.totalPurchased || 0)}</strong></article>
      <article><span>Saldo devedor</span><strong>${money.format(summary.openCredit || 0)}</strong></article>
      <article><span>Limite disponível</span><strong>${money.format(summary.availableCredit || 0)}</strong></article>
      <article><span>Vencido</span><strong>${money.format(summary.overdueCredit || 0)}</strong></article>
    </div>
    ${renderCustomerScoreCard(score)}
    <section class="customer-detail-section">
      <h3>Dados cadastrais</h3>
      <div class="customer-data-grid">
        <div><span>CPF</span><strong>${escapeHtml(customer.cpf || "-")}</strong></div>
        <div><span>RG</span><strong>${escapeHtml(customer.rg || "-")}</strong></div>
        <div><span>Telefone</span><strong>${escapeHtml(customer.whatsapp || "-")}</strong></div>
        <div><span>E-mail</span><strong>${escapeHtml(customer.email || "-")}</strong></div>
        <div><span>Nascimento</span><strong>${escapeHtml(formatDate(customer.birth) || "-")}</strong></div>
        <div><span>Limite</span><strong>${money.format(customer.limit || 0)}</strong></div>
        <div class="wide"><span>Endereço</span><strong>${escapeHtml([
          customer.address,
          customer.addressNumber,
          customer.district,
          customer.city,
          customer.state,
          customer.zip,
        ].filter(Boolean).join(", ") || "-")}</strong></div>
        <div class="wide"><span>Observações</span><strong>${escapeHtml(customer.notes || "-")}</strong></div>
      </div>
    </section>
    <section class="customer-detail-section">
      <h3>Compras realizadas</h3>
      ${sales.length ? `<div class="customer-history-list">${sales.map((sale) => `
        <div><strong>${escapeHtml(sale.id)}</strong><span>${escapeHtml(formatDateTime(sale.createdAt))}</span><span>${money.format(sale.total || 0)}</span><span>${sale.status === "cancelled" ? "Cancelada" : "Concluída"}</span></div>
      `).join("")}</div>` : '<p class="customer-detail-empty">Nenhuma compra registrada.</p>'}
    </section>
    <section class="customer-detail-section">
      <h3>Crediário e pagamentos</h3>
      ${receivables.length ? `<div class="customer-history-list">${receivables.map((item) => `
        <div><strong>${escapeHtml(item.saleId || "-")} · ${escapeHtml(item.installment || "-")}</strong><span>Vence ${escapeHtml(formatDate(item.dueDate))}</span><span>${money.format(receivableBalance(item))} em aberto</span><span>${escapeHtml(item.status || "-")}</span></div>
      `).join("")}</div>` : '<p class="customer-detail-empty">Nenhuma parcela registrada.</p>'}
    </section>
    <section class="customer-detail-section">
      <h3>Condicionais</h3>
      ${conditionals.length ? `<div class="customer-history-list">${conditionals.map((item) => `
        <div><strong>${escapeHtml(item.id || "-")}</strong><span>${escapeHtml(formatDateTime(item.createdAt))}</span><span>${(item.items || []).reduce((total, product) => total + Number(product.quantity || 0), 0)} peça(s)</span><span>${item.status === "finalized" ? "Finalizado" : "Em aberto"}</span></div>
      `).join("")}</div>` : '<p class="customer-detail-empty">Nenhum condicional registrado.</p>'}
    </section>
    <section class="customer-detail-section customer-audit-grid">
      <div>
        <h3>Histórico de situação</h3>
        ${statusHistory.length ? statusHistory.map((item) => `<p><strong>${escapeHtml(customerStatusLabel(item.previousStatus))} → ${escapeHtml(customerStatusLabel(item.newStatus))}</strong><br><small>${escapeHtml(item.reason || "Sem motivo informado")} · ${escapeHtml(item.userName || "-")} · ${escapeHtml(formatDateTime(item.createdAt))}</small></p>`).join("") : '<p class="customer-detail-empty">Sem alterações.</p>'}
      </div>
      <div>
        <h3>Histórico de limite</h3>
        ${limitHistory.length ? limitHistory.map((item) => `<p><strong>${money.format(item.previousLimit || 0)} → ${money.format(item.newLimit || 0)}</strong><br><small>${escapeHtml(item.userName || "-")} · ${escapeHtml(formatDateTime(item.createdAt))}</small></p>`).join("") : '<p class="customer-detail-empty">Sem alterações.</p>'}
      </div>
    </section>
  `;
}

function renderCustomerScoreCard(score) {
  if (!score) {
    return '<section class="customer-score-card loading"><span>Score do cliente</span><strong>Carregando...</strong></section>';
  }
  if (!score.available) {
    return `<section class="customer-score-card unavailable"><span>Score do cliente</span><strong>Não disponível</strong><small>${escapeHtml(score.reason || "Histórico insuficiente.")}</small></section>`;
  }
  const level = score.score >= 75 ? "good" : score.score >= 50 ? "regular" : "risk";
  return `
    <section class="customer-score-card ${level}">
      <div class="score-summary"><span class="score-indicator">${Number(score.score)}</span><div><span>Score do cliente</span><strong>${escapeHtml(score.classification)}</strong><small>${Number(score.score)}/100</small></div></div>
      <div><span>Comportamento no crediário</span><strong>${Number(score.creditPoints || 0).toFixed(0)} pts</strong><small>${score.overdueInstallments || 0} parcela(s) vencida(s)</small></div>
      <div><span>Compras diretas</span><strong>${score.directPurchasePoints || 0} pts</strong><small>${score.directPurchases || 0} compra(s) no período</small></div>
    </section>
  `;
}

function renderSuppliers() {
  els.supplierList.innerHTML = "";
  const term = normalize(els.supplierListSearch.value);
  const status = els.supplierStatusFilter.value;
  const financial = els.supplierFinancialFilter.value;
  const suppliers = db.suppliers.filter((supplier) => (status === "all" || supplier.status === status)
    && (financial === "all"
      || (financial === "open" && Number(supplier.openAmount || 0) > 0)
      || (financial === "overdue" && Number(supplier.overdueAmount || 0) > 0)
      || (financial === "credit" && Number(supplier.creditAvailable || 0) > 0))
    && (!term
      || normalize(supplier.name).includes(term)
      || normalize(supplier.tradeName).includes(term)
      || normalize(supplier.document || supplier.cnpj).includes(term)
      || normalize(supplier.phone).includes(term)
      || normalize(supplier.whatsapp).includes(term)
      || normalize(supplier.email).includes(term)));
  els.supplierActiveKpi.textContent = db.suppliers.filter((item) => item.status !== "deactivated").length;
  els.supplierOpenKpi.textContent = money.format(db.suppliers.reduce((total, item) => total + Number(item.openAmount || 0), 0));
  els.supplierOverdueKpi.textContent = money.format(db.suppliers.reduce((total, item) => total + Number(item.overdueAmount || 0), 0));
  els.supplierCreditKpi.textContent = money.format(db.suppliers.reduce((total, item) => total + Number(item.creditAvailable || 0), 0));
  if (!db.suppliers.length) {
    els.supplierList.innerHTML = `<tr><td colspan="8" class="empty-cell">Nenhum fornecedor cadastrado.</td></tr>`;
    return;
  }
  if (!suppliers.length) {
    els.supplierList.innerHTML = `<tr><td colspan="8" class="empty-cell">Nenhum fornecedor encontrado.</td></tr>`;
    return;
  }
  suppliers.forEach((supplier) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td><strong>${escapeHtml(supplier.name)}</strong><small>${escapeHtml(supplier.tradeName || supplier.city || "-")}</small></td>
      <td>${escapeHtml(supplier.document || supplier.cnpj || "-")}</td>
      <td><strong>${escapeHtml(supplier.whatsapp || supplier.phone || "-")}</strong><small>${escapeHtml(supplier.email || "-")}</small></td>
      <td>${money.format(supplier.openAmount || 0)}</td>
      <td>${money.format(supplier.overdueAmount || 0)}</td>
      <td>${money.format(supplier.creditAvailable || 0)}</td>
      <td><span class="status-pill ${supplier.status === "deactivated" ? "blocked" : "active"}">${supplier.status === "deactivated" ? "Desativado" : "Ativo"}</span></td>
      <td><div class="table-actions"></div></td>
    `;
    const actions = row.querySelector(".table-actions");
    actions.append(button("Visualizar", "icon-button", () => openSupplierDetail(supplier.id)));
    actions.append(button("Editar", "icon-button", () => editSupplier(supplier.id)));
    actions.append(button(supplier.status === "deactivated" ? "Reativar" : "Desativar", `icon-button ${supplier.status === "deactivated" ? "" : "danger-icon"}`, () => deleteSupplier(supplier.id)));
    els.supplierList.append(row);
  });
}

function renderSimpleLists() {
  const configs = {
    brands: { list: els.brandList, search: els.brandListSearch, columns: 2 },
    categories: { list: els.categoryList, search: els.categoryListSearch, columns: 2 },
    sizes: { list: els.sizeList, search: els.sizeListSearch, columns: 3 },
    colors: { list: els.colorList, search: els.colorListSearch, columns: 3 },
    expenseCategories: { list: els.expenseCategoryList, search: els.expenseCategoryListSearch, columns: 3 },
  };
  Object.entries(configs).forEach(([collection, config]) => {
    const term = normalize(config.search.value);
    const items = db[collection].filter((item) => !term || normalize(item.name).includes(term));
    config.list.innerHTML = items.length
      ? items.map((item) => `<tr>
          <td><strong>${escapeHtml(item.name)}</strong></td>
          ${config.columns === 3 ? `<td><span class="status-pill ${item.status === "deactivated" ? "blocked" : "active"}">${item.status === "deactivated" ? "Desativado" : "Ativo"}</span></td>` : ""}
          <td><div class="table-actions">
            <button class="icon-button" type="button" data-catalog-edit="${escapeHtml(item.id)}">Editar</button>
            <button class="icon-button ${item.status === "deactivated" ? "" : "danger-icon"}" type="button" data-catalog-status="${escapeHtml(item.id)}">${item.status === "deactivated" ? "Reativar" : "Desativar"}</button>
          </div></td>
        </tr>`).join("")
      : `<tr><td colspan="${config.columns}" class="empty-cell">Nenhum cadastro encontrado.</td></tr>`;
    config.list.querySelectorAll("[data-catalog-edit]").forEach((button) => button.addEventListener("click", () => editSimpleName(collection, button.dataset.catalogEdit)));
    config.list.querySelectorAll("[data-catalog-status]").forEach((button) => button.addEventListener("click", () => deleteSimpleName(collection, button.dataset.catalogStatus)));
  });
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
      <td><span class="status-pill ${user.active === false || user.blocked ? "blocked" : "active"}">${user.blocked ? "Bloqueado" : user.active === false ? "Inativo" : user.role === "admin" ? "Admin" : "Operador"}</span></td>
      <td><div class="table-actions"></div></td>
    `;
    const actions = row.querySelector(".table-actions");
    actions.append(button("Editar", "icon-button", () => editUser(user.id)));
    if (user.blocked) actions.append(button("Desbloquear", "icon-button", () => unlockUser(user.id)));
    if (user.active !== false) {
      actions.append(button("Desativar", "icon-button danger-icon", () => deleteUser(user.id)));
    }
    els.userList.append(row);
  });
}

function catalogFilterPayload() {
  return {
    query: els.catalogSearch.value.trim(),
    category: els.catalogCategoryFilter.value === "all" ? "" : els.catalogCategoryFilter.value,
    brand: els.catalogBrandFilter.value === "all" ? "" : els.catalogBrandFilter.value,
    size: els.catalogSizeFilter.value === "all" ? "" : els.catalogSizeFilter.value,
    color: els.catalogColorFilter.value === "all" ? "" : els.catalogColorFilter.value,
    minPrice: els.catalogMinPrice.value.trim(),
    maxPrice: els.catalogMaxPrice.value.trim(),
    order: els.catalogOrder.value || "name",
  };
}

function scheduleCatalogLoad() {
  clearTimeout(catalogLoadTimer);
  catalogLoadTimer = setTimeout(() => loadCatalog(true), 250);
}

async function loadCatalog(force = false) {
  if (!BACKEND_ENABLED || !session || catalogLoading) return;
  if (catalogLoaded && !force) {
    renderCatalog();
    return;
  }
  catalogLoading = true;
  catalogError = "";
  renderCatalog();
  const query = new URLSearchParams();
  Object.entries(catalogFilterPayload()).forEach(([key, value]) => {
    if (value !== "") query.set(key, value);
  });
  try {
    const response = await fetch(`/api/catalog/products?${query.toString()}`, { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      throw new Error(payload.error || "Não foi possível carregar o catálogo.");
    }
    catalogData = payload.data || { items: [], total: 0, filters: {}, query: {} };
    catalogLoaded = true;
  } catch (error) {
    console.warn(error);
    catalogError = error.message || "Não foi possível carregar o catálogo.";
    catalogData = { items: [], total: 0, filters: {}, query: {} };
    catalogLoaded = false;
  } finally {
    catalogLoading = false;
    renderCatalog();
  }
}

function renderCatalog() {
  if (!els.catalogList) return;
  const products = catalogData.items || [];
  els.catalogList.innerHTML = "";
  els.catalogList.classList.toggle("catalog-list-view", catalogViewMode === "list");
  els.catalogList.classList.toggle("catalog-grid-view", catalogViewMode === "grid");
  els.catalogList.classList.toggle("empty", catalogLoading || Boolean(catalogError) || products.length === 0);
  els.catalogGridViewButton.classList.toggle("active", catalogViewMode === "grid");
  els.catalogListViewButton.classList.toggle("active", catalogViewMode === "list");
  els.catalogCount.textContent = catalogLoading
    ? "Carregando produtos..."
    : `${products.length} produto${products.length === 1 ? "" : "s"} encontrado${products.length === 1 ? "" : "s"}`;
  if (catalogLoading) {
    els.catalogList.innerHTML = '<div class="catalog-state"><span class="catalog-spinner" aria-hidden="true"></span><strong>Carregando catálogo...</strong></div>';
    return;
  }
  if (catalogError) {
    const state = document.createElement("div");
    state.className = "catalog-state catalog-error-state";
    state.innerHTML = `<strong>${escapeHtml(catalogError)}</strong>`;
    state.append(button("Tentar novamente", "ghost", () => loadCatalog(true)));
    els.catalogList.append(state);
    return;
  }
  if (!products.length) {
    els.catalogList.innerHTML = '<div class="catalog-state"><strong>Nenhum produto disponível com os filtros selecionados.</strong></div>';
    return;
  }
  products.forEach((product) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "catalog-card";
    card.setAttribute("aria-label", `Ver detalhes de ${product.name}`);
    card.innerHTML = `
      ${product.photo ? `<img src="${escapeHtml(product.photo)}" alt="">` : '<div class="photo-placeholder" aria-hidden="true">Sem foto</div>'}
      <h3>${escapeHtml(product.name)}</h3>
      <small>${escapeHtml(product.category || "Sem categoria")}</small>
      <p>${escapeHtml(product.size || "-")} | ${escapeHtml(product.color || "-")} | ${escapeHtml(product.brand || "Sem marca")}</p>
      <strong>${money.format(Number(product.price || 0))}</strong>
      <span class="catalog-stock-tag ${product.availability === "last_unit" ? "last-unit" : ""}">
        <svg viewBox="0 0 24 24"><path d="m12 3 8 4.5v9L12 21l-8-4.5v-9L12 3Z"></path><path d="M4 7.5 12 12l8-4.5"></path><path d="M12 12v9"></path></svg>
        ${escapeHtml(product.availabilityLabel || "Disponível")}
      </span>
    `;
    card.addEventListener("click", () => openCatalogDetail(product.id));
    els.catalogList.append(card);
  });
}

function setCatalogView(mode) {
  catalogViewMode = mode;
  renderCatalog();
}

function clearCatalogFilters() {
  els.catalogSearch.value = "";
  els.catalogCategoryFilter.value = "all";
  els.catalogBrandFilter.value = "all";
  els.catalogSizeFilter.value = "all";
  els.catalogColorFilter.value = "all";
  els.catalogMinPrice.value = "";
  els.catalogMaxPrice.value = "";
  els.catalogOrder.value = "name";
  loadCatalog(true);
}

async function openCatalogDetail(productId) {
  els.catalogDetailModal.hidden = false;
  els.catalogDetailTitle.textContent = "Produto";
  els.catalogDetailContent.innerHTML = '<div class="catalog-state"><span class="catalog-spinner" aria-hidden="true"></span><strong>Carregando produto...</strong></div>';
  try {
    const response = await fetch(`/api/catalog/products/${encodeURIComponent(productId)}`, { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      throw new Error(payload.error || "Não foi possível carregar o produto.");
    }
    const product = payload.data;
    els.catalogDetailTitle.textContent = product.name || "Produto";
    els.catalogDetailContent.innerHTML = `
      <div class="catalog-detail-photo">
        ${product.photo ? `<img src="${escapeHtml(product.photo)}" alt="">` : '<div class="photo-placeholder">Sem foto</div>'}
      </div>
      <div class="catalog-detail-info">
        <span class="catalog-stock-tag ${product.availability === "last_unit" ? "last-unit" : ""}">${escapeHtml(product.availabilityLabel || "Disponível")}</span>
        <strong class="catalog-detail-price">${money.format(Number(product.price || 0))}</strong>
        <dl>
          <div><dt>Marca</dt><dd>${escapeHtml(product.brand || "Sem marca")}</dd></div>
          <div><dt>Categoria</dt><dd>${escapeHtml(product.category || "Sem categoria")}</dd></div>
          <div><dt>Tamanho</dt><dd>${escapeHtml(product.size || "-")}</dd></div>
          <div><dt>Cor</dt><dd>${escapeHtml(product.color || "-")}</dd></div>
        </dl>
        ${product.description ? `<p>${escapeHtml(product.description)}</p>` : ""}
      </div>
    `;
  } catch (error) {
    console.warn(error);
    els.catalogDetailContent.innerHTML = `<div class="catalog-state catalog-error-state"><strong>${escapeHtml(error.message || "Não foi possível carregar o produto.")}</strong></div>`;
  }
}

function closeCatalogDetail() {
  els.catalogDetailModal.hidden = true;
  els.catalogDetailContent.innerHTML = "";
}

async function generateOfficialDocument(type, sourceId = "", format = "a4", options = {}) {
  if (documentGenerationInProgress) return null;
  documentGenerationInProgress = true;
  try {
    const response = await fetch("/api/documents", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Idempotency-Key": createId(),
      },
      body: JSON.stringify({ type, sourceId, format, options }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return null;
      alert(payload.error || "Não foi possível gerar o documento.");
      return null;
    }
    const generated = payload.data;
    generatedDocuments = [
      generated,
      ...generatedDocuments.filter((entry) => entry.id !== generated.id),
    ];
    renderGeneratedDocuments();
    return generated;
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para gerar o documento.");
    return null;
  } finally {
    documentGenerationInProgress = false;
  }
}

async function exportCatalogPdf() {
  const printWindow = prepareDocumentWindow();
  if (!printWindow) return;
  const generated = await generateOfficialDocument(
    "catalog",
    "",
    "a4",
    { filters: catalogFilterPayload() },
  );
  if (generated) openOfficialDocument(generated, true, printWindow);
  else printWindow.close();
}

async function printProductLabel(productId) {
  const rawCopies = prompt("Quantidade de etiquetas:", "1");
  if (rawCopies === null) return;
  const copies = Number(rawCopies);
  if (!Number.isInteger(copies) || copies < 1 || copies > 50) {
    alert("Informe uma quantidade inteira entre 1 e 50.");
    return;
  }
  const printWindow = prepareDocumentWindow();
  if (!printWindow) return;
  const generated = await generateOfficialDocument(
    "product_labels",
    "",
    "thermal",
    { items: [{ productId, copies }] },
  );
  if (generated) openOfficialDocument(generated, true, printWindow);
  else printWindow.close();
}

async function loadGeneratedDocuments(force = false) {
  if (!BACKEND_ENABLED || !session || generatedDocumentsLoading) return;
  if (generatedDocuments.length && !force) {
    renderGeneratedDocuments();
    return;
  }
  generatedDocumentsLoading = true;
  renderGeneratedDocuments();
  try {
    const response = await fetch("/api/documents", { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      throw new Error(payload.error || "Não foi possível carregar os documentos.");
    }
    generatedDocuments = Array.isArray(payload.data) ? payload.data : [];
  } catch (error) {
    console.warn(error);
    generatedDocuments = [];
  } finally {
    generatedDocumentsLoading = false;
    renderGeneratedDocuments();
  }
}

function renderGeneratedDocuments() {
  if (!els.catalogDocumentsList) return;
  els.catalogDocumentsList.innerHTML = "";
  els.catalogDocumentsList.classList.toggle("empty", generatedDocumentsLoading || !generatedDocuments.length);
  if (generatedDocumentsLoading) {
    els.catalogDocumentsList.innerHTML = '<div class="catalog-state"><span class="catalog-spinner" aria-hidden="true"></span><strong>Carregando documentos...</strong></div>';
    return;
  }
  if (!generatedDocuments.length) {
    els.catalogDocumentsList.innerHTML = '<div class="catalog-state"><strong>Nenhum documento gerado.</strong></div>';
    return;
  }
  const typeLabels = {
    sale_receipt: "Comprovante de venda",
    conditional: "Condicional",
    exchange: "Troca",
    catalog: "Catálogo",
    product_labels: "Etiquetas",
  };
  generatedDocuments.forEach((entry) => {
    const row = window.document.createElement("article");
    row.className = "catalog-document-row";
    row.innerHTML = `
      <div>
        <strong>${escapeHtml(typeLabels[entry.documentType] || entry.documentType)}</strong>
        <small>${escapeHtml(entry.operationNumber || "Sem número")} · ${formatStoreDateTime(entry.generatedAt)}</small>
      </div>
      <span>${entry.secondCopy ? `${entry.copyNumber}ª via` : "Original"}</span>
      <div class="table-actions"></div>
    `;
    const actions = row.querySelector(".table-actions");
    actions.append(button("Visualizar", "ghost", () => openOfficialDocument(entry, false)));
    actions.append(button("2ª via", "primary", () => reprintOfficialDocument(entry.id)));
    els.catalogDocumentsList.append(row);
  });
}

async function reprintOfficialDocument(documentId) {
  const printWindow = prepareDocumentWindow();
  if (!printWindow) return;
  try {
    const response = await fetch(`/api/documents/${encodeURIComponent(documentId)}/reprint`, {
      method: "POST",
      headers: { "Idempotency-Key": createId() },
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) {
        printWindow.close();
        return;
      }
      alert(payload.error || "Não foi possível gerar a segunda via.");
      printWindow.close();
      return;
    }
    const generated = payload.data;
    generatedDocuments = [
      generated,
      ...generatedDocuments.filter((entry) => entry.id !== generated.id),
    ];
    renderGeneratedDocuments();
    openOfficialDocument(generated, true, printWindow);
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para gerar a segunda via.");
    printWindow.close();
  }
}

function officialDocumentHeader(documentData, title) {
  const store = documentData.snapshot?.store || {};
  const logo = store.logoUrl
    ? `<img class="document-logo" src="${escapeHtml(new URL(store.logoUrl, location.origin).href)}" alt="">`
    : "";
  return `
    <header class="document-header">
      ${logo}
      <div><h1>${escapeHtml(store.name || "Mova Sports")}</h1><p>${escapeHtml(title)}</p></div>
      <div class="document-meta">
        <strong>${escapeHtml(documentData.operationNumber || "")}</strong>
        <span>${formatStoreDateTime(documentData.generatedAt)}</span>
        ${documentData.secondCopy ? `<b>${documentData.copyNumber}ª VIA</b>` : ""}
      </div>
    </header>
  `;
}

function saleDocumentMarkup(documentData) {
  const sale = documentData.snapshot?.operation || {};
  const items = (sale.items || []).map((item) => `
    <tr>
      <td>${Number(item.quantity || 0)}x ${escapeHtml(item.name || "-")}<small>${escapeHtml([item.size, item.color, item.brand].filter(Boolean).join(" | "))}</small></td>
      <td>${money.format(Number(item.finalUnitPrice ?? item.practicedUnitPrice ?? 0))}</td>
      <td>${money.format(Number(item.netTotal ?? item.total ?? 0))}</td>
    </tr>
  `).join("");
  const payments = (sale.payments || []).map((payment) => `
    <li><span>${escapeHtml(paymentLabels[payment.method] || payment.method || "-")}</span><strong>${money.format(Number(payment.amount || 0))}</strong></li>
  `).join("");
  return `
    ${officialDocumentHeader(documentData, "Comprovante de venda")}
    <section class="document-customer"><strong>Cliente:</strong> ${escapeHtml(sale.customerName || "Venda simples")}<br><strong>Data:</strong> ${formatStoreDateTime(sale.createdAt)}</section>
    <table><thead><tr><th>Item</th><th>Unitário</th><th>Total</th></tr></thead><tbody>${items}</tbody></table>
    <section class="document-totals">
      <p><span>Subtotal</span><strong>${money.format(Number(sale.subtotal || 0))}</strong></p>
      <p><span>Desconto</span><strong>${money.format(Number(sale.discount || 0))}</strong></p>
      <p class="grand-total"><span>Total</span><strong>${money.format(Number(sale.total || 0))}</strong></p>
    </section>
    <ul class="document-payments">${payments}</ul>
  `;
}

function conditionalDocumentMarkup(documentData) {
  const conditional = documentData.snapshot?.operation || {};
  const items = (conditional.items || []).map((item) => `
    <tr><td>${escapeHtml(item.name || "-")}<small>${escapeHtml([item.size, item.color, item.brand].filter(Boolean).join(" | "))}</small></td><td>${Number(item.quantity || 0)}</td><td>${money.format(Number(item.unitPrice || 0))}</td></tr>
  `).join("");
  return `
    ${officialDocumentHeader(documentData, "Termo de condicional")}
    <section class="document-customer"><strong>Cliente:</strong> ${escapeHtml(conditional.customerName || "-")}<br><strong>Saída:</strong> ${formatStoreDateTime(conditional.checkedOutAt || conditional.createdAt)}<br><strong>Retorno previsto:</strong> ${formatDate(conditional.expectedReturnDate)}</section>
    <table><thead><tr><th>Produto</th><th>Qtd.</th><th>Referência</th></tr></thead><tbody>${items}</tbody></table>
    <p class="document-note">Os produtos permanecem vinculados a este condicional até o retorno ou a finalização da operação.</p>
  `;
}

function exchangeDocumentMarkup(documentData) {
  const exchange = documentData.snapshot?.operation || {};
  const returned = (exchange.returnedItems || []).map((item) => `
    <tr><td>${escapeHtml(item.name || "-")}</td><td>${Number(item.quantity || 0)}</td><td>${money.format(Number(item.creditTotal || 0))}</td></tr>
  `).join("");
  const delivered = (exchange.newItems || []).map((item) => `
    <tr><td>${escapeHtml(item.name || "-")}</td><td>${Number(item.quantity || 0)}</td><td>${money.format(Number(item.netTotal || 0))}</td></tr>
  `).join("");
  return `
    ${officialDocumentHeader(documentData, "Comprovante de troca")}
    <section class="document-customer"><strong>Cliente:</strong> ${escapeHtml(exchange.customerName || "-")}<br><strong>Venda de origem:</strong> ${escapeHtml(exchange.saleId || "-")}<br><strong>Data:</strong> ${formatStoreDateTime(exchange.createdAt)}</section>
    <h2>Itens devolvidos</h2>
    <table><thead><tr><th>Produto</th><th>Qtd.</th><th>Crédito</th></tr></thead><tbody>${returned || '<tr><td colspan="3">Nenhum item.</td></tr>'}</tbody></table>
    <h2>Itens entregues</h2>
    <table><thead><tr><th>Produto</th><th>Qtd.</th><th>Total</th></tr></thead><tbody>${delivered || '<tr><td colspan="3">Nenhum item.</td></tr>'}</tbody></table>
    <section class="document-totals"><p class="grand-total"><span>Diferença</span><strong>${money.format(Number(exchange.differenceAmount || 0))}</strong></p></section>
  `;
}

function catalogDocumentMarkup(documentData) {
  const catalog = documentData.snapshot?.operation || {};
  const cards = (catalog.items || []).map((product) => `
    <article class="print-catalog-card">
      ${product.photo ? `<img src="${escapeHtml(product.photo)}" alt="">` : '<div class="placeholder">Sem foto</div>'}
      <h2>${escapeHtml(product.name || "-")}</h2>
      <p>${escapeHtml([product.size, product.color, product.brand].filter(Boolean).join(" | "))}</p>
      <strong>${money.format(Number(product.price || 0))}</strong>
      <span>${escapeHtml(product.availabilityLabel || "Disponível")}</span>
    </article>
  `).join("");
  return `
    ${officialDocumentHeader(documentData, "Catálogo de produtos")}
    <p class="document-note">${Number(catalog.total || 0)} produto${Number(catalog.total || 0) === 1 ? "" : "s"} disponível${Number(catalog.total || 0) === 1 ? "" : "is"} no momento da emissão.</p>
    <main class="print-catalog-grid">${cards || '<p>Nenhum produto disponível.</p>'}</main>
  `;
}

function labelDocumentMarkup(documentData) {
  const labels = documentData.snapshot?.operation?.items || [];
  return labels.flatMap((item) => Array.from({ length: Number(item.copies || 0) }, () => `
    <article class="product-label">
      <strong>${escapeHtml(item.name || "-")}</strong>
      <span>${escapeHtml([item.size, item.color].filter(Boolean).join(" | "))}</span>
      <div class="barcode">${item.barcodeSvg || ""}</div>
      <b>${money.format(Number(item.price || 0))}</b>
    </article>
  `)).join("");
}

function officialDocumentBody(documentData) {
  if (documentData.documentType === "sale_receipt") return saleDocumentMarkup(documentData);
  if (documentData.documentType === "conditional") return conditionalDocumentMarkup(documentData);
  if (documentData.documentType === "exchange") return exchangeDocumentMarkup(documentData);
  if (documentData.documentType === "catalog") return catalogDocumentMarkup(documentData);
  return labelDocumentMarkup(documentData);
}

function prepareDocumentWindow() {
  const printWindow = window.open("", "_blank");
  if (!printWindow) {
    alert("Permita pop-ups para visualizar ou imprimir o documento.");
    return null;
  }
  printWindow.document.write('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Preparando documento</title></head><body style="font:14px Arial;padding:24px">Preparando documento...</body></html>');
  printWindow.document.close();
  return printWindow;
}

function openOfficialDocument(documentData, autoPrint = false, targetWindow = null) {
  const printWindow = targetWindow || prepareDocumentWindow();
  if (!printWindow) return;
  const thermal = documentData.format === "thermal";
  printWindow.document.open();
  printWindow.document.write(`
    <!doctype html>
    <html lang="pt-BR">
    <head>
      <meta charset="utf-8">
      <title>${escapeHtml(documentData.filename || "Documento Mova Sports")}</title>
      <style>
        *{box-sizing:border-box}body{margin:0;padding:${thermal ? "10px" : "28px"};font:14px Arial,sans-serif;color:#17212f;background:#fff}
        body.thermal{width:80mm;max-width:100%;margin:auto}.document-header{display:flex;align-items:center;gap:14px;border-bottom:2px solid #17212f;padding-bottom:14px;margin-bottom:18px}
        .document-logo{width:72px;height:58px;object-fit:contain}.document-header h1{margin:0;font-size:22px}.document-header p{margin:4px 0 0;color:#66758a;font-weight:700}
        .document-meta{margin-left:auto;text-align:right;display:grid;gap:4px}.document-meta b{color:#ee3f75}.document-customer{line-height:1.7;margin-bottom:16px}
        table{width:100%;border-collapse:collapse;margin:12px 0 18px}th,td{text-align:left;padding:8px;border-bottom:1px solid #d7e0ea}td small{display:block;color:#66758a;margin-top:3px}
        .document-totals{margin-left:auto;max-width:320px}.document-totals p,.document-payments li{display:flex;justify-content:space-between;gap:16px;margin:7px 0}.grand-total{font-size:18px;border-top:2px solid #17212f;padding-top:10px}
        .document-payments{list-style:none;padding:12px 0;margin:0;border-top:1px dashed #aeb9c8}.document-note{padding:12px;background:#f4f6f9;border-radius:6px;color:#526176;font-weight:700}
        .print-catalog-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.print-catalog-card{break-inside:avoid;border:1px solid #d7e0ea;border-radius:8px;padding:10px}
        .print-catalog-card img,.print-catalog-card .placeholder{width:100%;aspect-ratio:1/1;object-fit:cover;background:#f4f6f9;display:grid;place-items:center;border-radius:6px}
        .print-catalog-card h2{font-size:15px;margin:10px 0 5px}.print-catalog-card p{color:#66758a}.print-catalog-card strong{font-size:18px}.print-catalog-card span{display:block;margin-top:8px;color:#159655;font-weight:700}
        .product-label{width:72mm;min-height:32mm;padding:3mm;border:1px dashed #aeb9c8;break-inside:avoid;display:grid;grid-template-columns:1fr auto;gap:2mm;align-items:center}
        .product-label>span{font-size:11px}.product-label .barcode{grid-column:1/-1;text-align:center}.product-label .barcode svg{width:100%;height:17mm}.product-label>b{font-size:16px}
        body.thermal .document-header{display:grid;text-align:center}body.thermal .document-logo{margin:auto}body.thermal .document-meta{margin:0;text-align:center}
        body.thermal th,body.thermal td{padding:6px 2px;font-size:12px}@page{margin:${thermal ? "4mm" : "12mm"}}@media print{body{padding:0}.product-label{border:0}}
      </style>
    </head>
    <body class="${thermal ? "thermal" : "a4"}">
      ${officialDocumentBody(documentData)}
      ${autoPrint ? '<script>window.addEventListener("load",()=>window.print());<\/script>' : ""}
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
    const available = availableProductStock(product);
    const productStatus = stockStatus(product).key;
    const matchesQuery = !query || normalize(product.name).includes(query) || normalize(product.barcode).includes(query);
    const matchesCategory = category === "all" || product.category === category;
    const matchesBrand = brand === "all" || product.brand === brand;
    const matchesStatus = status === "all" || productStatus === status;
    return available > 0
      && matchesQuery
      && matchesCategory
      && matchesBrand
      && matchesStatus;
  });
  els.stockList.innerHTML = "";
  if (!products.length) {
    els.stockList.innerHTML = `<tr><td colspan="12" class="empty-cell">Nenhum produto disponível encontrado.</td></tr>`;
    els.stockFooter.textContent = "Mostrando 0 produtos";
    renderInventoryHistory();
    return;
  }
  products.forEach((product) => {
    const statusInfo = stockStatus(product);
    const real = Math.max(0, Number(product.stock || 0));
    const reserved = Math.max(0, Number(product.reservedStock || openConditionalReservedQty(product.id)));
    const available = availableProductStock(product);
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${escapeHtml(product.barcode || "-")}</td>
      <td>
        <div class="stock-product-cell">
          ${product.photo ? `<img src="${product.photo}" alt="">` : `<div class="stock-product-photo"></div>`}
          <div><strong>${escapeHtml(product.name || "-")}</strong><small>${available} disponível</small></div>
        </div>
      </td>
      <td>${escapeHtml(product.category || "-")}</td>
      <td>${escapeHtml(product.brand || "-")}</td>
      <td>${escapeHtml(product.size || "-")}</td>
      <td>${escapeHtml(product.color || "-")}</td>
      <td><strong>${real}</strong></td>
      <td><strong>${reserved}</strong></td>
      <td><span class="stock-badge ${statusInfo.key}"><strong>${available}</strong><small>${statusInfo.label}</small></span></td>
      <td>${money.format(product.cost || 0)}</td>
      <td>${money.format(product.price || 0)}</td>
      <td><div class="table-actions"></div></td>
    `;
    const actions = row.querySelector(".table-actions");
    actions.append(button("Histórico", "icon-button", () => {
      selectedInventoryProductId = product.id;
      renderInventoryHistory();
      els.inventoryHistoryList.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }));
    actions.append(button("Editar", "stock-menu-button", () => editProduct(product.id)));
    els.stockList.append(row);
  });
  els.stockFooter.innerHTML = `
    <span>Mostrando 1 a ${products.length} de ${products.length} produto${products.length === 1 ? "" : "s"}</span>
    <div class="stock-pagination"><button type="button" disabled>Anterior</button><button type="button" class="active">1</button><button type="button" disabled>Próximo</button></div>
  `;
  renderInventoryHistory();
}

function stockStatus(product) {
  const available = availableProductStock(product);
  if (available <= 0) return { key: "empty", label: "Sem estoque" };
  if (available <= (product.minStock || 0)) return { key: "low", label: "Estoque baixo" };
  return { key: "ok", label: "Em estoque" };
}

function inventoryMovementLabel(type) {
  return {
    opening_balance: "Saldo inicial",
    entry: "Entrada",
    entry_cancellation: "Cancelamento de entrada",
    supplier_return: "Devolução ao fornecedor",
    supplier_return_cancellation: "Cancelamento de devolução",
    sale: "Venda",
    sale_cancellation: "Cancelamento de venda",
    customer_return: "Devolução de cliente",
    conditional_reserve: "Reserva condicional",
    conditional_release: "Liberação condicional",
    inventory_adjustment: "Ajuste de inventário",
  }[type] || type || "Movimentação";
}

function renderInventoryHistory() {
  if (!els.inventoryHistoryList || !els.inventoryHistoryCaption) return;
  const selectedProduct = db.products.find(
    (product) => product.id === selectedInventoryProductId,
  );
  const movements = (db.inventoryMovements || [])
    .filter(
      (movement) => !selectedInventoryProductId
        || movement.productId === selectedInventoryProductId,
    )
    .sort(
      (first, second) => String(second.createdAt || "")
        .localeCompare(String(first.createdAt || "")),
    )
    .slice(0, 50);
  els.inventoryHistoryCaption.textContent = selectedProduct
    ? `Movimentações de ${selectedProduct.name}`
    : "Todas as movimentações de estoque";
  els.inventoryHistoryClear.hidden = !selectedInventoryProductId;
  if (!movements.length) {
    els.inventoryHistoryList.innerHTML = '<p class="inventory-history-empty">Nenhuma movimentação encontrada.</p>';
    return;
  }
  els.inventoryHistoryList.innerHTML = movements.map((movement) => {
    const realDelta = Number(movement.realDelta || 0);
    const reservedDelta = Number(movement.reservedDelta || 0);
    const delta = realDelta || reservedDelta;
    const deltaLabel = `${delta > 0 ? "+" : ""}${delta}`;
    const deltaClass = delta > 0 ? "in" : "out";
    return `
      <article class="inventory-history-row">
        <div class="inventory-history-icon ${deltaClass}" aria-hidden="true">${delta > 0 ? "↓" : "↑"}</div>
        <div class="inventory-history-main">
          <strong>${escapeHtml(inventoryMovementLabel(movement.movementType))}</strong>
          <span>${escapeHtml(movement.productName || "-")} | ${escapeHtml(movement.barcode || "-")}</span>
          <small>${escapeHtml(movement.referenceType || "-")} ${escapeHtml(movement.referenceId || "")}</small>
        </div>
        <div class="inventory-history-balance">
          <strong class="${deltaClass}">${deltaLabel}</strong>
          <span>Real ${Number(movement.realAfter || 0)}</span>
          <small>${Number(movement.reservedAfter || 0)} reserv. | ${Number(movement.availableAfter || 0)} disp.</small>
        </div>
      </article>
    `;
  }).join("");
}

function physicalInventoryStatusLabel(status) {
  return {
    in_progress: "Em andamento",
    finalized: "Finalizado",
    cancelled: "Cancelado",
  }[status] || status || "-";
}

function physicalInventoryTypeLabel(type) {
  return type === "general" ? "Geral" : "Parcial";
}

function mergePhysicalInventorySummary(inventory) {
  if (!inventory?.id) return;
  const summary = { ...inventory };
  delete summary.items;
  db.inventories = [
    summary,
    ...(db.inventories || []).filter((item) => item.id !== summary.id),
  ].sort((first, second) => Number(second.number || 0) - Number(first.number || 0));
  persistLocalOnly();
}

function openInventoryCreate() {
  inventoryCreateKey = "";
  els.inventoryCreateForm.reset();
  els.inventoryType.value = "general";
  els.inventoryBrand.innerHTML = [
    '<option value="">Todas</option>',
    ...activeCatalogItems("brands").map((item) => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.name)}</option>`),
  ].join("");
  els.inventoryCategory.innerHTML = [
    '<option value="">Todas</option>',
    ...activeCatalogItems("categories").map((item) => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.name)}</option>`),
  ].join("");
  els.inventoryProduct.innerHTML = [
    '<option value="">Todos do filtro</option>',
    ...db.products.filter((item) => item.active !== false).map((item) => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.name)} | ${escapeHtml(item.barcode || "-")}</option>`),
  ].join("");
  updateInventoryCreateFields();
  els.inventoryCreatePanel.hidden = false;
  els.inventoryCreatePanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function closeInventoryCreate() {
  els.inventoryCreatePanel.hidden = true;
  inventoryCreateKey = "";
}

function updateInventoryCreateFields() {
  const partial = els.inventoryType.value === "partial";
  document.querySelectorAll(".inventory-partial-field").forEach((field) => {
    field.hidden = !partial;
  });
}

async function createPhysicalInventory(event) {
  event.preventDefault();
  const partial = els.inventoryType.value === "partial";
  const scope = partial ? {
    brandId: els.inventoryBrand.value,
    categoryId: els.inventoryCategory.value,
    gender: els.inventoryGender.value,
    barcode: els.inventoryScopeBarcode.value.trim(),
    productIds: els.inventoryProduct.value ? [els.inventoryProduct.value] : [],
  } : {};
  if (partial && !scope.brandId && !scope.categoryId && !scope.gender && !scope.barcode && !scope.productIds.length) {
    return alert("Defina ao menos um filtro para o inventário parcial.");
  }
  inventoryCreateKey ||= createId();
  const submit = els.inventoryCreateForm.querySelector('button[type="submit"]');
  submit.disabled = true;
  try {
    const response = await fetch("/api/inventories", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Idempotency-Key": inventoryCreateKey,
      },
      body: JSON.stringify({ type: els.inventoryType.value, scope }),
    });
    const payload = await response.json();
    if (handleUnauthorized(response, payload)) return;
    if (!response.ok) throw new Error(payload.error || "Não foi possível abrir o inventário.");
    mergePhysicalInventorySummary(payload.data);
    closeInventoryCreate();
    await openPhysicalInventory(payload.data.id);
  } catch (error) {
    alert(error.message);
  } finally {
    submit.disabled = false;
  }
}

function renderPhysicalInventories() {
  if (!els.inventoryList) return;
  const inventories = db.inventories || [];
  els.inventoryOpenCount.textContent = inventories.filter((item) => item.status === "in_progress").length;
  els.inventoryFinalizedCount.textContent = inventories.filter((item) => item.status === "finalized").length;
  els.inventoryCancelledCount.textContent = inventories.filter((item) => item.status === "cancelled").length;
  els.inventoryDivergenceCount.textContent = inventories
    .filter((item) => item.status === "finalized")
    .reduce((total, item) => total + Number(item.divergenceCount || 0), 0);

  const search = normalize(els.inventorySearch.value);
  const type = els.inventoryTypeFilter.value;
  const status = els.inventoryStatusFilter.value;
  const selectedUser = els.inventoryUserFilter.value;
  const startDate = els.inventoryStartFilter.value;
  const endDate = els.inventoryEndFilter.value;
  const responsibleUsers = [...new Map(inventories
    .filter((item) => item.startedById)
    .map((item) => [item.startedById, item.startedByName || "Usuário"])).entries()]
    .sort((first, second) => first[1].localeCompare(second[1], "pt-BR"));
  els.inventoryUserFilter.innerHTML = [
    '<option value="">Todos</option>',
    ...responsibleUsers.map(([id, name]) => `<option value="${escapeHtml(id)}">${escapeHtml(name)}</option>`),
  ].join("");
  els.inventoryUserFilter.value = responsibleUsers.some(([id]) => id === selectedUser) ? selectedUser : "";
  const user = els.inventoryUserFilter.value;
  const rows = inventories.filter((item) => (
    (!type || item.type === type)
    && (!status || item.status === status)
    && (!user || item.startedById === user)
    && (!startDate || storeOperationalDateKey(item.startedAt) >= startDate)
    && (!endDate || storeOperationalDateKey(item.startedAt) <= endDate)
    && (!search || normalize(`${item.code} ${item.number} ${item.scopeLabel} ${item.startedByName}`).includes(search))
  ));
  els.inventoryList.innerHTML = rows.map((item) => {
    const counted = Number(item.countedCount || 0);
    const total = Number(item.productCount || 0);
    return `
      <tr>
        <td><strong>${escapeHtml(item.code || `INV${item.number}`)}</strong></td>
        <td><strong>${physicalInventoryTypeLabel(item.type)}</strong><small>${escapeHtml(item.scopeLabel || "-")}</small></td>
        <td>${escapeHtml(formatDateTime(item.startedAt))}</td>
        <td>${escapeHtml(item.startedByName || "-")}</td>
        <td><strong>${counted}/${total}</strong><small>${Number(item.uncountedCount ?? Math.max(0, total - counted))} pendente(s)</small></td>
        <td><span class="inventory-status ${escapeHtml(item.status)}">${physicalInventoryStatusLabel(item.status)}</span></td>
        <td><button class="ghost inventory-view-button" type="button" data-inventory-id="${escapeHtml(item.id)}">Visualizar</button></td>
      </tr>
    `;
  }).join("");
  els.inventoryListEmpty.hidden = rows.length > 0;
  els.inventoryList.querySelectorAll("[data-inventory-id]").forEach((buttonElement) => {
    buttonElement.addEventListener("click", () => openPhysicalInventory(buttonElement.dataset.inventoryId));
  });
  if (selectedPhysicalInventoryId && physicalInventoryDetail) renderPhysicalInventoryDetail();
}

async function openPhysicalInventory(inventoryId) {
  try {
    const response = await fetch(`/api/inventories/${encodeURIComponent(inventoryId)}`, { cache: "no-store" });
    const payload = await response.json();
    if (handleUnauthorized(response, payload)) return;
    if (!response.ok) throw new Error(payload.error || "Não foi possível abrir o inventário.");
    selectedPhysicalInventoryId = inventoryId;
    physicalInventoryDetail = payload.data;
    inventoryFinalizeKey = "";
    els.inventoryListPanel.hidden = true;
    els.inventoryDetailPanel.hidden = false;
    renderPhysicalInventoryDetail();
  } catch (error) {
    alert(error.message);
  }
}

function closeInventoryDetail() {
  selectedPhysicalInventoryId = "";
  physicalInventoryDetail = null;
  inventoryFinalizeKey = "";
  els.inventoryDetailPanel.hidden = true;
  els.inventoryListPanel.hidden = false;
  renderPhysicalInventories();
}

function currentInventoryDivergence(item) {
  if (item.countedQuantity === null || item.countedQuantity === undefined) return null;
  return Number(item.divergence ?? (Number(item.countedQuantity) - Number(item.expectedQuantity || 0)));
}

function renderPhysicalInventoryDetail() {
  const inventory = physicalInventoryDetail;
  if (!inventory || !els.inventoryDetailPanel || els.inventoryDetailPanel.hidden) return;
  const inProgress = inventory.status === "in_progress";
  const items = inventory.items || [];
  const counted = items.filter((item) => item.countedQuantity !== null && item.countedQuantity !== undefined).length;
  const liveDivergences = items.filter((item) => currentInventoryDivergence(item) !== 0 && currentInventoryDivergence(item) !== null);
  els.inventoryDetailTitle.textContent = `${inventory.code} | Inventário ${physicalInventoryTypeLabel(inventory.type)}`;
  els.inventoryDetailMeta.textContent = `${inventory.scopeLabel || "-"} | Aberto por ${inventory.startedByName || "-"} em ${formatDateTime(inventory.startedAt)}`;
  els.inventoryDetailStatus.className = `inventory-status ${inventory.status}`;
  els.inventoryDetailStatus.textContent = physicalInventoryStatusLabel(inventory.status);
  els.inventoryDetailSummary.innerHTML = `
    <article><span>Produtos</span><strong>${items.length}</strong></article>
    <article><span>Contados</span><strong>${counted}</strong></article>
    <article><span>Pendentes</span><strong>${Math.max(0, items.length - counted)}</strong></article>
    <article><span>Divergências</span><strong>${inProgress ? liveDivergences.length : Number(inventory.divergenceCount || 0)}</strong></article>
    <article><span>Impacto</span><strong>${money.format(Number(inventory.positiveImpact || 0) - Number(inventory.negativeImpact || 0))}</strong></article>
  `;
  els.inventoryCountingTools.hidden = !inProgress;
  els.inventoryFinalizeArea.hidden = !inProgress;
  if (!inProgress) els.inventoryNotes.value = inventory.generalNotes || inventory.cancellationReason || "";

  const filter = els.inventoryItemFilter.value;
  const filtered = items.filter((item) => {
    const divergence = currentInventoryDivergence(item);
    if (filter === "uncounted") return divergence === null;
    if (filter === "divergent") return divergence !== null && divergence !== 0;
    if (filter === "positive") return divergence > 0;
    if (filter === "negative") return divergence < 0;
    if (filter === "matched") return divergence === 0;
    return true;
  });
  els.inventoryItemList.innerHTML = filtered.map((item) => {
    const divergence = currentInventoryDivergence(item);
    const divergenceLabel = divergence === null ? "Não contado" : divergence > 0 ? `+${divergence}` : String(divergence);
    const divergenceClass = divergence === null ? "pending" : divergence > 0 ? "positive" : divergence < 0 ? "negative" : "matched";
    const countControl = inProgress ? `
      <div class="inventory-count-control">
        <input type="number" min="0" step="1" value="${item.countedQuantity ?? ""}" data-inventory-count="${escapeHtml(item.id)}" aria-label="Contagem de ${escapeHtml(item.productName)}">
        <button class="ghost" type="button" data-inventory-save="${escapeHtml(item.id)}">Salvar</button>
      </div>
    ` : `<strong>${Number(item.countedQuantity || 0)}</strong>`;
    return `
      <tr>
        <td><strong>${escapeHtml(item.productName)}</strong><small>${escapeHtml(item.barcode || "-")} | ${escapeHtml(item.size || "-")} | ${escapeHtml(item.color || "-")} | ${escapeHtml(item.brand || "Sem marca")}</small></td>
        <td><strong>${Number(item.initialExpected || 0)}</strong><small>Real ${Number(item.initialReal || 0)} | Reservado ${Number(item.initialReserved || 0)}</small></td>
        <td><strong>${Number(item.expectedQuantity || 0)}</strong><small>Real ${Number(item.currentReal ?? 0)} | Reservado ${Number(item.currentReserved ?? 0)}</small></td>
        <td>${countControl}</td>
        <td><span class="inventory-divergence ${divergenceClass}">${divergenceLabel}</span></td>
        <td><small>${item.countedByName ? `${escapeHtml(item.countedByName)} | ${escapeHtml(formatDateTime(item.countedAt))}` : "Sem contagem"}</small></td>
      </tr>
    `;
  }).join("");
  els.inventoryItemsEmpty.hidden = filtered.length > 0;
  els.inventoryItemList.querySelectorAll("[data-inventory-save]").forEach((buttonElement) => {
    buttonElement.addEventListener("click", () => {
      const itemId = buttonElement.dataset.inventorySave;
      const input = els.inventoryItemList.querySelector(`[data-inventory-count="${CSS.escape(itemId)}"]`);
      savePhysicalInventoryCount(itemId, input?.value);
    });
  });
}

async function savePhysicalInventoryCount(itemId, rawQuantity) {
  const inventory = physicalInventoryDetail;
  const item = inventory?.items?.find((entry) => entry.id === itemId);
  if (!item) return;
  const quantity = Number(rawQuantity);
  if (!Number.isInteger(quantity) || quantity < 0) return alert("Informe uma quantidade inteira igual ou maior que zero.");
  try {
    const response = await fetch(`/api/inventories/${encodeURIComponent(inventory.id)}/items/${encodeURIComponent(itemId)}/count`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quantity, version: item.countVersion }),
    });
    const payload = await response.json();
    if (handleUnauthorized(response, payload)) return;
    if (!response.ok) throw new Error(payload.error || "Não foi possível salvar a contagem.");
    const saved = payload.data.item;
    physicalInventoryDetail.items = physicalInventoryDetail.items.map((entry) => entry.id === saved.id ? saved : entry);
    Object.assign(physicalInventoryDetail, payload.data.inventory);
    mergePhysicalInventorySummary(physicalInventoryDetail);
    renderPhysicalInventoryDetail();
  } catch (error) {
    alert(error.message);
    if (error.message.includes("outro usuário")) await openPhysicalInventory(inventory.id);
  }
}

async function countInventoryBarcode(event) {
  event.preventDefault();
  const code = els.inventoryBarcode.value.trim();
  if (!code || !physicalInventoryDetail) return;
  try {
    const response = await fetch(`/api/inventories/${encodeURIComponent(physicalInventoryDetail.id)}/barcode?code=${encodeURIComponent(code)}`, { cache: "no-store" });
    const payload = await response.json();
    if (handleUnauthorized(response, payload)) return;
    if (!response.ok) throw new Error(payload.error || "Produto não encontrado neste inventário.");
    const item = payload.data;
    const quantity = item.countedQuantity === null || item.countedQuantity === undefined ? 1 : Number(item.countedQuantity) + 1;
    await savePhysicalInventoryCount(item.id, quantity);
    els.inventoryBarcode.value = "";
    els.inventoryBarcode.focus();
  } catch (error) {
    alert(error.message);
    els.inventoryBarcode.select();
  }
}

async function finalizePhysicalInventory() {
  const inventory = physicalInventoryDetail;
  if (!inventory) return;
  const pending = (inventory.items || []).filter((item) => item.countedQuantity === null || item.countedQuantity === undefined).length;
  if (pending) return alert(`Ainda existem ${pending} produtos não contados.`);
  const divergences = (inventory.items || []).filter((item) => currentInventoryDivergence(item) !== 0).length;
  if (divergences && !els.inventoryNotes.value.trim()) return alert("Informe uma observação para finalizar com divergências.");
  if (!confirm(divergences ? `Confirmar ${divergences} ajuste(s) de estoque?` : "Finalizar este inventário sem divergências?")) return;
  inventoryFinalizeKey ||= createId();
  els.inventoryFinalizeButton.disabled = true;
  try {
    const response = await fetch(`/api/inventories/${encodeURIComponent(inventory.id)}/finalize`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Idempotency-Key": inventoryFinalizeKey,
      },
      body: JSON.stringify({ notes: els.inventoryNotes.value.trim() }),
    });
    const payload = await response.json();
    if (handleUnauthorized(response, payload)) return;
    if (!response.ok) throw new Error(payload.error || "Não foi possível finalizar o inventário.");
    physicalInventoryDetail = payload.data;
    mergePhysicalInventorySummary(payload.data);
    await syncFromServer();
    await openPhysicalInventory(inventory.id);
  } catch (error) {
    alert(error.message);
  } finally {
    els.inventoryFinalizeButton.disabled = false;
  }
}

async function cancelPhysicalInventory() {
  const inventory = physicalInventoryDetail;
  if (!inventory) return;
  const reason = prompt("Informe o motivo do cancelamento:");
  if (reason === null) return;
  if (!reason.trim()) return alert("O motivo do cancelamento é obrigatório.");
  if (!confirm("Cancelar este inventário? Nenhum ajuste de estoque será realizado.")) return;
  try {
    const response = await fetch(`/api/inventories/${encodeURIComponent(inventory.id)}/cancel`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reason: reason.trim() }),
    });
    const payload = await response.json();
    if (handleUnauthorized(response, payload)) return;
    if (!response.ok) throw new Error(payload.error || "Não foi possível cancelar o inventário.");
    physicalInventoryDetail = payload.data;
    mergePhysicalInventorySummary(payload.data);
    renderPhysicalInventoryDetail();
  } catch (error) {
    alert(error.message);
  }
}

function renderSaleProducts() {
  const query = normalize(els.saleProductSearch.value);
  const products = db.products.filter((product) => availableProductStock(product) > 0 && (!query || normalize(product.name).startsWith(query) || normalize(product.barcode).includes(query)));
  els.saleProductList.innerHTML = "";
  els.saleProductList.classList.toggle("empty", products.length === 0);
  if (!products.length) {
    els.saleProductList.textContent = "Nenhum produto disponível encontrado.";
    return;
  }
  products.slice(0, 8).forEach((product) => {
    const available = availableProductStock(product);
    const row = document.createElement("article");
    row.className = "sale-product-row";
    row.innerHTML = `
      ${product.photo ? `<img src="${product.photo}" alt="">` : `<div class="sale-product-photo"></div>`}
      <div><strong>${escapeHtml(product.name)}</strong><small>${escapeHtml(productListMeta(product))}</small></div>
      <strong>${money.format(product.price)}</strong>
      <div class="table-actions"></div>
    `;
    row.querySelector(".table-actions").append(button("Adicionar", "sale-add-product", () => addToCart(product.id), available <= cartQty(product.id)));
    els.saleProductList.append(row);
  });
}

function addToCart(productId) {
  const product = db.products.find((item) => item.id === productId);
  if (!product || availableProductStock(product) <= cartQty(product.id)) return alert("Produto sem estoque disponível. Verifique condicionais em aberto.");
  const existing = cart.find((item) => item.productId === product.id);
  if (existing) existing.quantity += 1;
  else cart.push({
    productId: product.id,
    barcode: product.barcode,
    name: product.name,
    brand: product.brand,
    quantity: 1,
    practicedUnitPrice: Number(product.price || 0),
    unitDiscount: 0,
    unitAddition: 0,
  });
  pendingSaleKey = "";
  renderAll();
}

function cartQty(productId) {
  return cart.find((item) => item.productId === productId)?.quantity || 0;
}

function changeCartQty(productId, delta) {
  const item = cart.find((entry) => entry.productId === productId);
  const product = db.products.find((entry) => entry.id === productId);
  if (!item || !product) return;
  if (item.conditionalItemId) {
    alert("A quantidade originada do condicional deve ser mantida.");
    return;
  }
  item.quantity += delta;
  if (item.quantity <= 0) cart = cart.filter((entry) => entry.productId !== productId);
  const available = availableProductStock(product);
  if (item.quantity > available) item.quantity = available;
  pendingSaleKey = "";
  renderAll();
}

function openConditionalReservedQty(productId) {
  return (db.conditionals || [])
    .filter((doc) => doc.status !== "finalized" && doc.status !== "cancelled")
    .flatMap((doc) => doc.items || [])
    .filter((item) => item.productId === productId)
    .reduce((total, item) => total + conditionalItemPending(item), 0);
}

function availableProductStock(product) {
  return Math.max(0, Number(product?.stock || 0) - openConditionalReservedQty(product?.id));
}

function productStockLabel(product) {
  const reserved = openConditionalReservedQty(product.id);
  const available = availableProductStock(product);
  return reserved > 0 ? `Disponível: ${available} | Condicional: ${reserved}` : `Estoque: ${Number(product.stock || 0)}`;
}

function productListMeta(product) {
  return `${product.barcode || "-"} | ${product.size || "-"} | ${product.color || "-"} | ${productStockLabel(product)}`;
}

function renderCart() {
  els.cartList.innerHTML = "";
  els.cartList.classList.toggle("empty", cart.length === 0);
  if (!cart.length) {
    els.cartList.innerHTML = `<div class="sale-cart-empty"><span>▢</span><strong>Nenhum item adicionado</strong><small>Adicione produtos para iniciar a venda</small></div>`;
  }
  cart.forEach((item) => {
    const finalUnitPrice = saleItemFinalUnitPrice(item);
    const row = document.createElement("article");
    row.className = "sale-cart-row";
    row.innerHTML = `
      <span>${cart.indexOf(item) + 1}</span>
      <strong>${escapeHtml(item.name)}</strong>
      <span>${item.quantity}</span>
      <span>${money.format(finalUnitPrice)}</span>
      <b>${money.format(item.quantity * finalUnitPrice)}</b>
    `;
    const actions = document.createElement("div");
    actions.className = "sale-cart-actions";
    if (!item.conditionalItemId) {
      actions.append(button("+", "ghost", () => changeCartQty(item.productId, 1)));
      actions.append(button("-", "danger", () => changeCartQty(item.productId, -1)));
    }
    actions.append(button("Ajustar", "ghost sale-item-adjust-button", () => openSaleItemAdjustment(item.productId)));
    row.append(actions);
    els.cartList.append(row);
  });
  if (!els.paymentRows.children.length) addPaymentRow("cash", false);
  const paymentRow = els.paymentRows.querySelectorAll(".payment-row");
  if (paymentRow.length === 1) {
    const amountInput = paymentRow[0].querySelector(".pay-amount");
    const tenderedInput = paymentRow[0].querySelector(".pay-tendered");
    const previousAmount = readNumber(amountInput.value);
    const previousTendered = readNumber(tenderedInput.value);
    amountInput.value = fixed(saleTotal());
    if (paymentRow[0].querySelector(".pay-method").value === "cash" && previousTendered <= previousAmount) {
      tenderedInput.value = fixed(saleTotal());
    }
  }
  renderCartTotalOnly();
}

function saleItemFinalUnitPrice(item) {
  return Math.max(0, round(
    Number(item.practicedUnitPrice ?? item.unitPrice ?? 0)
      - Number(item.unitDiscount || 0)
      + Number(item.unitAddition || 0),
  ));
}

function openSaleItemAdjustment(productId) {
  const item = cart.find((entry) => entry.productId === productId);
  if (!item) return;
  els.saleItemAdjustmentProductId.value = item.productId;
  els.saleItemAdjustmentName.textContent = item.name;
  els.saleItemPracticedPrice.value = fixed(Number(item.practicedUnitPrice ?? item.unitPrice ?? 0));
  els.saleItemDiscount.value = fixed(Number(item.unitDiscount || 0));
  els.saleItemAddition.value = fixed(Number(item.unitAddition || 0));
  els.saleItemAdjustmentError.hidden = true;
  els.saleItemAdjustmentError.textContent = "";
  els.saleItemAdjustmentBackdrop.hidden = false;
  els.saleItemPracticedPrice.focus();
}

function closeSaleItemAdjustment() {
  els.saleItemAdjustmentBackdrop.hidden = true;
  els.saleItemAdjustmentForm.reset();
}

function saveSaleItemAdjustment(event) {
  event.preventDefault();
  const item = cart.find((entry) => entry.productId === els.saleItemAdjustmentProductId.value);
  if (!item) return closeSaleItemAdjustment();
  const practiced = readNumber(els.saleItemPracticedPrice.value);
  const discount = readNumber(els.saleItemDiscount.value);
  const addition = readNumber(els.saleItemAddition.value);
  if (practiced < 0 || discount < 0 || addition < 0 || practiced - discount + addition < 0) {
    els.saleItemAdjustmentError.textContent = "Os ajustes não podem resultar em valor negativo.";
    els.saleItemAdjustmentError.hidden = false;
    return;
  }
  item.practicedUnitPrice = practiced;
  item.unitDiscount = discount;
  item.unitAddition = addition;
  pendingSaleKey = "";
  closeSaleItemAdjustment();
  renderAll();
}

function renderConditionalPanels() {
  if (els.conditionalCurrentCard) els.conditionalCurrentCard.hidden = conditionalView !== "new";
  if (els.conditionalOpenPanel) els.conditionalOpenPanel.hidden = conditionalView !== "list";
  if (els.conditionalFinalizePanel && conditionalView !== "detail") {
    els.conditionalFinalizePanel.hidden = true;
    els.conditionalFinalizePanel.innerHTML = "";
  }
}

function renderConditionalProducts() {
  if (!els.conditionalProductList) return;
  const query = normalize(els.conditionalProductSearch.value);
  const products = db.products.filter((product) => availableProductStock(product) > 0 && (!query || normalize(product.name).startsWith(query) || normalize(product.barcode).includes(query)));
  els.conditionalProductList.innerHTML = "";
  els.conditionalProductList.classList.toggle("empty", products.length === 0);
  if (!products.length) {
    els.conditionalProductList.textContent = "Nenhum produto com estoque disponível encontrado.";
    return;
  }
  products.slice(0, 8).forEach((product) => {
    const available = availableProductStock(product);
    const row = document.createElement("article");
    row.className = "sale-product-row";
    row.innerHTML = `
      ${product.photo ? `<img src="${product.photo}" alt="">` : `<div class="sale-product-photo"></div>`}
      <div><strong>${escapeHtml(product.name)}</strong><small>${escapeHtml(productListMeta(product))}</small></div>
      <strong>${money.format(product.price)}</strong>
      <div class="table-actions"></div>
    `;
    row.querySelector(".table-actions").append(button("Adicionar", "sale-add-product", () => addToConditionalCart(product.id), conditionalView !== "new" || available <= conditionalCartQty(product.id)));
    els.conditionalProductList.append(row);
  });
}

function addToConditionalCart(productId) {
  if (conditionalView !== "new") return alert("Clique em Novo para iniciar um condicional.");
  const product = db.products.find((item) => item.id === productId);
  if (!product || availableProductStock(product) <= conditionalCartQty(product.id)) return alert("Produto sem estoque disponível. Verifique condicionais em aberto.");
  const existing = conditionalCart.find((item) => item.productId === product.id);
  if (existing) existing.quantity += 1;
  else conditionalCart.push({ productId: product.id, barcode: product.barcode, name: product.name, brand: product.brand, quantity: 1, unitCost: product.cost, unitPrice: product.price });
  renderAll();
}

function conditionalCartQty(productId) {
  return conditionalCart.find((item) => item.productId === productId)?.quantity || 0;
}

function changeConditionalCartQty(productId, delta) {
  const item = conditionalCart.find((entry) => entry.productId === productId);
  const product = db.products.find((entry) => entry.id === productId);
  if (!item || !product) return;
  item.quantity += delta;
  if (item.quantity <= 0) conditionalCart = conditionalCart.filter((entry) => entry.productId !== productId);
  const available = availableProductStock(product);
  if (item.quantity > available) item.quantity = available;
  renderAll();
}

function conditionalTotal() {
  return conditionalCart.reduce((total, item) => total + Number(item.quantity || 0) * Number(item.unitPrice || 0), 0);
}

function renderConditionalCart() {
  if (!els.conditionalCartList) return;
  els.conditionalCartList.innerHTML = "";
  els.conditionalCartList.classList.toggle("empty", conditionalCart.length === 0);
  if (!conditionalCart.length) {
    els.conditionalCartList.innerHTML = `<div class="sale-cart-empty"><span>□</span><strong>Nenhum item adicionado</strong><small>Adicione produtos para enviar em condicional</small></div>`;
  }
  conditionalCart.forEach((item) => {
    const row = document.createElement("article");
    row.className = "sale-cart-row";
    row.innerHTML = `
      <span>${conditionalCart.indexOf(item) + 1}</span>
      <strong>${escapeHtml(item.name)}</strong>
      <span>${item.quantity}</span>
      <span>${money.format(item.unitPrice)}</span>
      <b>${money.format(item.quantity * item.unitPrice)}</b>
    `;
    const actions = document.createElement("div");
    actions.className = "sale-cart-actions";
    actions.append(button("+", "ghost", () => changeConditionalCartQty(item.productId, 1)));
    actions.append(button("-", "danger", () => changeConditionalCartQty(item.productId, -1)));
    row.append(actions);
    els.conditionalCartList.append(row);
  });
  if (els.conditionalTotal) els.conditionalTotal.textContent = money.format(conditionalTotal());
}

function startNewConditional() {
  conditionalView = "new";
  selectedConditionalId = "";
  conditionalCart = [];
  if (els.conditionalCustomerSearch) els.conditionalCustomerSearch.value = "";
  renderAll();
}

function clearConditional() {
  conditionalCart = [];
  selectedConditionalId = "";
  conditionalView = "list";
  if (els.conditionalCustomerSearch) els.conditionalCustomerSearch.value = "";
  renderAll();
}

async function saveConditional() {
  if (!conditionalCart.length) return alert("Adicione produtos ao condicional.");
  const customer = findActiveCustomerByName(els.conditionalCustomerSearch.value.trim());
  if (!customer) return alert("Somente cliente ativo e cadastrado pode receber condicional.");
  const doc = {
    customerId: customer.id,
    items: conditionalCart.map((item) => ({
      productId: item.productId,
      quantity: item.quantity,
    })),
  };
  if (!BACKEND_ENABLED) return showBackendRequiredMessage();
  try {
    const response = await fetch("/api/conditionals", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Idempotency-Key": createId() },
      body: JSON.stringify(doc),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      alert(payload.error || "Não foi possível salvar o condicional.");
      return;
    }
    upsertConditional(payload.data);
    await refreshInventoryMovements();
    persistLocalOnly();
    clearConditional();
    renderAll();
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para salvar o condicional.");
  }
}

function upsertConditional(doc) {
  if (!doc?.id) return;
  db.conditionals = [doc, ...db.conditionals.filter((item) => item.id !== doc.id)];
}

function customerForConditional(doc) {
  return db.customers.find((customer) => customer.id === doc.customerId || normalize(customer.name) === normalize(doc.customerName));
}

function conditionalItemPending(item) {
  if (item?.pendingQuantity !== undefined && item?.pendingQuantity !== null) {
    return Math.max(0, Number(item.pendingQuantity || 0));
  }
  return Math.max(
    0,
    Number(item?.quantity || 0)
      - Number(item?.returnedQuantity || 0)
      - Number(item?.soldQuantity || 0),
  );
}

function conditionalItemActionable(item) {
  if (item?.actionableQuantity !== undefined && item?.actionableQuantity !== null) {
    return Math.max(0, Number(item.actionableQuantity || 0));
  }
  return Math.max(0, conditionalItemPending(item) - Number(item?.pendingSaleQuantity || 0));
}

function conditionalPendingPieces(doc) {
  if (doc?.pendingPieces !== undefined && doc?.pendingPieces !== null) {
    return Math.max(0, Number(doc.pendingPieces || 0));
  }
  return (doc.items || []).reduce((total, item) => total + conditionalItemPending(item), 0);
}

function conditionalPendingValue(doc) {
  if (doc?.pendingValue !== undefined && doc?.pendingValue !== null) {
    return Math.max(0, Number(doc.pendingValue || 0));
  }
  return round((doc.items || []).reduce(
    (total, item) => total + conditionalItemPending(item) * Number(item.unitPrice || 0),
    0,
  ));
}

function effectiveConditionalStatus(doc) {
  if (doc.status === "cancelled" || doc.status === "finalized") return doc.status;
  if (conditionalPendingPieces(doc) > 0 && String(doc.expectedReturnDate || "") < todayIso) return "overdue";
  return "open";
}

function conditionalStatusLabel(status) {
  return {
    open: "Em aberto",
    overdue: "Em atraso",
    finalized: "Finalizado",
    cancelled: "Cancelado",
  }[status] || "Em aberto";
}

function renderConditionalSummary() {
  const conditionals = db.conditionals || [];
  const open = conditionals.filter((doc) => effectiveConditionalStatus(doc) === "open");
  const overdue = conditionals.filter((doc) => effectiveConditionalStatus(doc) === "overdue");
  const active = [...open, ...overdue];
  els.conditionalOpenCount.textContent = String(open.length);
  els.conditionalOverdueCount.textContent = String(overdue.length);
  els.conditionalPieceCount.textContent = String(active.reduce(
    (total, doc) => total + conditionalPendingPieces(doc),
    0,
  ));
  els.conditionalValue.textContent = money.format(active.reduce(
    (total, doc) => total + conditionalPendingValue(doc),
    0,
  ));
}

function renderConditionalOpenList() {
  if (!els.conditionalOpenList) return;
  renderConditionalSummary();
  const query = normalize(els.conditionalOpenSearch?.value || "");
  const statusFilter = els.conditionalStatusFilter?.value || "active";
  const start = els.conditionalStartFilter?.value || "";
  const end = els.conditionalEndFilter?.value || "";
  const items = (db.conditionals || []).filter((item) => {
    const customer = customerForConditional(item);
    const status = effectiveConditionalStatus(item);
    const searchText = normalize([
      item.id,
      item.conditionalNumber,
      item.customerName,
      item.customerCpf || customer?.cpf,
      item.customerPhone || customer?.whatsapp || customer?.phone,
    ].join(" "));
    const date = String(item.checkedOutAt || item.createdAt || "").slice(0, 10);
    if (query && !searchText.includes(query)) return false;
    if (statusFilter === "active" && !["open", "overdue"].includes(status)) return false;
    if (statusFilter !== "all" && statusFilter !== "active" && status !== statusFilter) return false;
    if (start && date < start) return false;
    if (end && date > end) return false;
    return true;
  }).sort((left, right) => String(
    right.checkedOutAt || right.createdAt || "",
  ).localeCompare(String(left.checkedOutAt || left.createdAt || "")));
  els.conditionalOpenList.innerHTML = "";
  els.conditionalOpenList.classList.toggle("empty", items.length === 0);
  if (!items.length) {
    els.conditionalOpenList.textContent = "Nenhum condicional encontrado para os filtros informados.";
    return;
  }
  items.forEach((doc) => {
    const status = effectiveConditionalStatus(doc);
    const pieces = conditionalPendingPieces(doc);
    const customer = customerForConditional(doc);
    const row = document.createElement("article");
    row.className = "conditional-open-row";
    row.innerHTML = `
      <div><strong>${escapeHtml(doc.id)}</strong><small>${formatDateTime(doc.checkedOutAt || doc.createdAt)}</small></div>
      <div><strong>${escapeHtml(doc.customerName || "-")}</strong><small>${escapeHtml(doc.customerCpf || customer?.cpf || "-")} | ${escapeHtml(doc.customerPhone || customer?.whatsapp || customer?.phone || "-")}</small></div>
      <div><strong>${pieces} peça${pieces === 1 ? "" : "s"}</strong><small>${money.format(conditionalPendingValue(doc))}</small></div>
      <span class="conditional-status ${status}">${conditionalStatusLabel(status)}</span>
      <div class="table-actions"></div>
    `;
    row.querySelector(".table-actions").append(button("Visualizar", "primary small-action", () => {
      selectedConditionalId = doc.id;
      conditionalView = "detail";
      renderAll();
    }));
    els.conditionalOpenList.append(row);
  });
}

function renderConditionalFinalizePanel() {
  if (!els.conditionalFinalizePanel) return;
  if (conditionalView !== "detail") {
    els.conditionalFinalizePanel.hidden = true;
    els.conditionalFinalizePanel.innerHTML = "";
    return;
  }
  const doc = (db.conditionals || []).find((item) => item.id === selectedConditionalId);
  if (!doc) {
    els.conditionalFinalizePanel.hidden = true;
    els.conditionalFinalizePanel.innerHTML = "";
    return;
  }
  els.conditionalFinalizePanel.hidden = false;
  const status = effectiveConditionalStatus(doc);
  const rows = (doc.items || []).map((item) => `
    <div class="conditional-finalize-row" data-item-id="${escapeHtml(item.id || "")}">
      <span>
        <strong>${escapeHtml(item.name)}</strong>
        <small>${escapeHtml(item.barcode || "-")} | ${escapeHtml(item.size || "-")} | ${escapeHtml(item.color || "-")}</small>
        <small>Enviado: ${Number(item.quantity || 0)} | Devolvido: ${Number(item.returnedQuantity || 0)} | Vendido: ${Number(item.soldQuantity || 0)} | Pendente: ${conditionalItemPending(item)}</small>
      </span>
      ${conditionalItemActionable(item) > 0 ? `
        <label class="field">Devolver<input class="conditional-return-quantity" type="number" min="0" max="${conditionalItemActionable(item)}" step="1" value="0"></label>
        <label class="field">Comprar<input class="conditional-purchase-quantity" type="number" min="0" max="${conditionalItemActionable(item)}" step="1" value="0"></label>
      ` : `
        <span>${Number(item.pendingSaleQuantity || 0) > 0 ? "Aguardando venda" : "Concluído"}</span>
        <span></span>
      `}
      <b>${money.format(conditionalItemPending(item) * Number(item.unitPrice || 0))}</b>
    </div>
  `).join("");
  const history = (doc.returns || []).map((event) => {
    const returned = (event.items || []).reduce((total, item) => total + Number(item.returnedQuantity || 0), 0);
    const purchase = (event.items || []).reduce((total, item) => total + Number(item.purchaseQuantity || 0), 0);
    return `
      <div class="conditional-history-row">
        <span>${formatDateTime(event.createdAt)}</span>
        <span>${returned} devolvida${returned === 1 ? "" : "s"} | ${purchase} para venda</span>
        <strong>${event.status === "awaiting_sale" ? "Venda pendente" : "Concluído"}</strong>
      </div>
    `;
  }).join("");
  const hasActionable = (doc.items || []).some((item) => conditionalItemActionable(item) > 0);
  const hasPendingSale = (doc.items || []).some((item) => Number(item.pendingSaleQuantity || 0) > 0);
  els.conditionalFinalizePanel.innerHTML = `
    <div class="section-title tight">
      <div><h2>${escapeHtml(doc.id)} | ${escapeHtml(doc.customerName || "-")}</h2><span class="conditional-status ${status}">${conditionalStatusLabel(status)}</span></div>
      <button class="ghost" type="button" id="closeConditionalFinalizeButton">Voltar</button>
    </div>
    <div class="conditional-detail-meta">
      <div><span>Saída</span><strong>${formatDateTime(doc.checkedOutAt || doc.createdAt)}</strong></div>
      <div><span>Retorno previsto</span><strong>${formatDate(doc.expectedReturnDate)}</strong></div>
      <div><span>Responsável</span><strong>${escapeHtml(doc.responsibleUserName || "-")}</strong></div>
      <div><span>Saldo</span><strong>${conditionalPendingPieces(doc)} peças | ${money.format(conditionalPendingValue(doc))}</strong></div>
    </div>
    <p class="conditional-detail-help">Informe apenas as quantidades que retornaram agora e as que o cliente decidiu comprar.</p>
    <div class="conditional-finalize-list">${rows}</div>
    <div class="conditional-finalize-actions">
      <button class="ghost" type="button" id="printConditionalButton">Imprimir</button>
      ${hasActionable ? '<button class="ghost" type="button" id="finishConditionalEmptyButton">Devolver todo o saldo</button><button class="primary" type="button" id="finishConditionalSaleButton">Registrar retorno</button>' : ""}
      ${hasPendingSale ? '<button class="primary" type="button" id="continueConditionalSaleButton">Continuar venda</button>' : ""}
      ${conditionalPendingPieces(doc) === 0 && status !== "cancelled" ? '<button class="danger" type="button" id="cancelConditionalButton">Cancelar</button>' : ""}
    </div>
    <div class="conditional-history">
      <strong>Histórico</strong>
      ${history || '<span class="conditional-detail-help">Nenhum retorno registrado.</span>'}
    </div>
  `;
  els.conditionalFinalizePanel.querySelector("#closeConditionalFinalizeButton").addEventListener("click", () => {
    selectedConditionalId = "";
    conditionalView = "list";
    renderAll();
  });
  els.conditionalFinalizePanel.querySelector("#printConditionalButton")?.addEventListener("click", () => printConditional(doc));
  els.conditionalFinalizePanel.querySelector("#finishConditionalEmptyButton")?.addEventListener("click", () => {
    els.conditionalFinalizePanel.querySelectorAll(".conditional-finalize-row").forEach((row) => {
      const item = (doc.items || []).find((entry) => entry.id === row.dataset.itemId);
      const returned = row.querySelector(".conditional-return-quantity");
      const purchase = row.querySelector(".conditional-purchase-quantity");
      if (returned && item) returned.value = String(conditionalItemActionable(item));
      if (purchase) purchase.value = "0";
    });
  });
  els.conditionalFinalizePanel.querySelector("#finishConditionalSaleButton")?.addEventListener("click", finishConditional);
  els.conditionalFinalizePanel.querySelector("#continueConditionalSaleButton")?.addEventListener("click", () => continueConditionalSale(doc));
  els.conditionalFinalizePanel.querySelector("#cancelConditionalButton")?.addEventListener("click", () => cancelConditional(doc));
}

async function finishConditional() {
  const doc = (db.conditionals || []).find((item) => item.id === selectedConditionalId);
  if (!doc) return;
  const items = [...els.conditionalFinalizePanel.querySelectorAll(".conditional-finalize-row")]
    .map((row) => ({
      conditionalItemId: row.dataset.itemId,
      returnedQuantity: Math.max(0, Math.floor(readNumber(row.querySelector(".conditional-return-quantity")?.value || 0))),
      purchaseQuantity: Math.max(0, Math.floor(readNumber(row.querySelector(".conditional-purchase-quantity")?.value || 0))),
    }))
    .filter((item) => item.returnedQuantity + item.purchaseQuantity > 0);
  if (!items.length) return alert("Informe ao menos uma quantidade devolvida ou destinada à compra.");
  if (!BACKEND_ENABLED) return showBackendRequiredMessage();
  try {
    const response = await fetch(`/api/conditionals/${encodeURIComponent(doc.id)}/returns`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Idempotency-Key": createId() },
      body: JSON.stringify({ items }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      alert(payload.error || "Não foi possível registrar o retorno.");
      return;
    }
    upsertConditional(payload.data.conditional);
    mergeInventoryMovements(payload.data.inventoryMovements || []);
    persistLocalOnly();
    if (payload.data.saleDraft) {
      moveConditionalItemsToSale(payload.data.conditional, payload.data.saleDraft);
      selectedConditionalId = "";
      conditionalView = "list";
      activateSubtab("nova-venda");
      alert("Retorno registrado. As peças escolhidas foram enviadas para a venda atual.");
    } else {
      selectedConditionalId = payload.data.conditional.id;
      conditionalView = "detail";
      alert("Retorno registrado.");
    }
    renderAll();
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para registrar o retorno.");
  }
}

function continueConditionalSale(doc) {
  const pendingReturn = [...(doc.returns || [])].reverse().find((event) => event.status === "awaiting_sale");
  if (!pendingReturn) return alert("Não foi encontrada uma venda pendente para este condicional.");
  const items = (pendingReturn.items || []).filter((item) => Number(item.purchaseQuantity || 0) > 0).map((item) => {
    const source = (doc.items || []).find((entry) => entry.id === item.conditionalItemId);
    return {
      conditionalItemId: item.conditionalItemId,
      productId: item.productId,
      quantity: Number(item.purchaseQuantity || 0),
      practicedUnitPrice: Number(source?.unitPrice || 0),
      unitDiscount: 0,
      unitAddition: 0,
    };
  });
  moveConditionalItemsToSale(doc, {
    conditionalId: doc.id,
    conditionalReturnId: pendingReturn.id,
    customerId: doc.customerId,
    customerName: doc.customerName,
    items,
  });
  selectedConditionalId = "";
  conditionalView = "list";
  activateSubtab("nova-venda");
  renderAll();
}

async function cancelConditional(doc) {
  const reason = prompt("Informe o motivo do cancelamento:");
  if (!reason?.trim()) return;
  try {
    const response = await fetch(`/api/conditionals/${encodeURIComponent(doc.id)}/cancel`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reason: reason.trim() }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      alert(payload.error || "Não foi possível cancelar o condicional.");
      return;
    }
    upsertConditional(payload.data);
    conditionalView = "list";
    selectedConditionalId = "";
    persistLocalOnly();
    renderAll();
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para cancelar o condicional.");
  }
}

async function printConditional(doc) {
  const printWindow = prepareDocumentWindow();
  if (!printWindow) return;
  const generated = await generateOfficialDocument(
    "conditional",
    doc.id,
    "a4",
  );
  if (generated) openOfficialDocument(generated, true, printWindow);
  else printWindow.close();
}

function moveConditionalItemsToSale(doc, saleDraft) {
  pendingConditionalSaleDraft = saleDraft;
  els.saleCustomerSearch.value = saleDraft.customerName || doc.customerName || "";
  cart = [];
  (saleDraft.items || []).forEach((item) => {
    const product = db.products.find((entry) => entry.id === item.productId);
    const source = (doc.items || []).find((entry) => entry.id === item.conditionalItemId);
    if (!product || Number(item.quantity || 0) <= 0) return;
    cart.push({
      conditionalItemId: item.conditionalItemId,
      productId: product.id,
      barcode: product.barcode,
      name: product.name,
      brand: source?.brand || product.brand,
      quantity: Number(item.quantity || 0),
      practicedUnitPrice: Number(item.practicedUnitPrice ?? source?.unitPrice ?? product.price ?? 0),
      unitDiscount: Number(item.unitDiscount || 0),
      unitAddition: Number(item.unitAddition || 0),
    });
  });
  pendingSaleKey = "";
}

function addPaymentRow(method = "cash", rerender = true) {
  const row = document.createElement("div");
  row.className = "payment-row";
  row.innerHTML = `
    <label class="field">Forma<select class="pay-method">${salePaymentOptionsMarkup()}</select></label>
    <label class="field">Valor<input class="pay-amount" type="number" min="0.01" step="0.01"></label>
    <label class="field pay-tendered-field">Valor entregue<input class="pay-tendered" type="number" min="0" step="0.01"></label>
    <button class="danger remove-pay" type="button">X</button>
  `;
  const select = row.querySelector(".pay-method");
  const directOption = [...select.options].find((option) => option.value === method);
  const cardOption = saleCardModalities.find((modality) => modality.method === method);
  select.value = directOption ? method : cardOption ? `card:${cardOption.cardModalityId}` : "cash";
  row.querySelector(".pay-amount").value = fixed(saleTotal());
  row.querySelector(".pay-tendered").value = fixed(saleTotal());
  row.addEventListener("input", () => {
    pendingSaleKey = "";
    updateSalePaymentRow(row);
    renderStoreCreditDuePreview();
    renderCartTotalOnly();
  });
  row.querySelector(".remove-pay").addEventListener("click", () => {
    row.remove();
    pendingSaleKey = "";
    renderStoreCreditDuePreview();
    renderCartTotalOnly();
  });
  els.paymentRows.append(row);
  updateSalePaymentRow(row);
  renderStoreCreditDuePreview();
  if (rerender) renderCartTotalOnly();
}

function updateSalePaymentRow(row) {
  const cash = row.querySelector(".pay-method").value === "cash";
  row.querySelector(".pay-tendered-field").hidden = !cash;
}

function renderCartTotalOnly() {
  els.saleTotal.textContent = money.format(saleTotal());
  if (els.saleChange) {
    const change = readPayments()
      .filter((payment) => payment.method === "cash")
      .reduce((total, payment) => total + Math.max(0, payment.tenderedAmount - payment.amount), 0);
    els.saleChange.textContent = money.format(round(change));
  }
}

function readPayments() {
  return [...els.paymentRows.querySelectorAll(".payment-row")].map((row) => {
    const selected = row.querySelector(".pay-method").value;
    const amount = readNumber(row.querySelector(".pay-amount").value);
    if (selected.startsWith("card:")) {
      const cardModalityId = selected.slice(5);
      const modality = saleCardModalities.find((item) => item.cardModalityId === cardModalityId);
      return {
        method: modality?.method || "",
        amount,
        cardModalityId,
        installments: Number(modality?.installments || 1),
      };
    }
    return {
      method: selected,
      amount,
      tenderedAmount: selected === "cash"
        ? readNumber(row.querySelector(".pay-tendered").value)
        : amount,
      installments: selected === "storeCredit"
        ? Math.max(1, Math.floor(readNumber(els.storeCreditInstallments.value)))
        : 1,
    };
  }).filter((payment) => payment.amount > 0);
}

function addCalendarMonthsIso(value, months) {
  const [year, month, day] = String(value || "").split("-").map(Number);
  if (!year || !month || !day) return "";
  const targetMonth = month - 1 + Number(months || 0);
  const targetYear = year + Math.floor(targetMonth / 12);
  const normalizedMonth = ((targetMonth % 12) + 12) % 12;
  const lastDay = new Date(Date.UTC(targetYear, normalizedMonth + 1, 0)).getUTCDate();
  return [
    String(targetYear).padStart(4, "0"),
    String(normalizedMonth + 1).padStart(2, "0"),
    String(Math.min(day, lastDay)).padStart(2, "0"),
  ].join("-");
}

function renderStoreCreditDuePreview() {
  if (!els.storeCreditDuePreview) return;
  const hasStoreCredit = readPayments().some((payment) => payment.method === "storeCredit");
  if (!hasStoreCredit) {
    els.storeCreditDuePreview.textContent = "Selecione o crediário para visualizar os vencimentos.";
    return;
  }
  const installments = Math.min(3, Math.max(1, Math.floor(readNumber(els.storeCreditInstallments.value))));
  const firstDue = els.storeCreditFirstDueDate.value || addCalendarMonthsIso(todayIso, 1);
  const dates = Array.from({ length: installments }, (_, index) => addCalendarMonthsIso(firstDue, index));
  els.storeCreditDuePreview.textContent = `Vencimentos: ${dates.map(formatDate).join(" · ")}`;
}

function saleSubtotal() {
  return round(cart.reduce((total, item) => total + item.quantity * saleItemFinalUnitPrice(item), 0));
}

function saleTotal() {
  return Math.max(0, round(
    saleSubtotal()
      + readNumber(els.saleAddition.value)
      - readNumber(els.saleDiscount.value),
  ));
}

async function finishSale() {
  if (!cart.length) return alert("Adicione produtos.");
  const total = saleTotal();
  const payments = readPayments();
  if (Math.abs(sum(payments, "amount") - total) > 0.01) return alert("Pagamentos precisam fechar com o total.");
  if (payments.some((payment) => !payment.method)) return alert("Selecione uma modalidade de cartão válida.");
  if (payments.some((payment) => payment.method === "cash" && payment.tenderedAmount < payment.amount)) {
    return alert("O valor entregue em dinheiro não pode ser menor que o valor devido.");
  }
  const customer = findCustomerByName(els.saleCustomerSearch.value.trim());
  const storeCredit = payments.filter((payment) => payment.method === "storeCredit").reduce((value, payment) => value + payment.amount, 0);
  let authorizeCreditLimit = false;
  if (els.saleCustomerSearch.value.trim() && !customer) return alert("Selecione um cliente válido ou deixe o campo vazio para venda simples.");
  if (storeCredit > 0 && !customer) return alert("Crediário exige cliente cadastrado.");
  if (storeCredit > 0 && customer) {
    if (customer.status === "blocked") return alert("Cliente bloqueado para crediário.");
    if (customer.isDefault) return alert("Crediário exige cliente identificado.");
    const installments = Math.max(1, Math.floor(readNumber(els.storeCreditInstallments.value)));
    if (installments > 3) return alert("Crediário permite no máximo 3 parcelas.");
    if (!els.storeCreditFirstDueDate.value) return alert("Informe o primeiro vencimento do crediário.");
    const creditStats = customerCreditStats(customer.id);
    if (creditStats.overdueCount > 0 && !confirm("O cliente possui parcelas atrasadas. Deseja continuar a venda?")) return;
    const open = customerDebt(customer.id).open;
    if (open + storeCredit > customer.limit) {
      if (!confirm("O limite de crédito será aumentado para comportar esta venda. Deseja autorizar?")) return;
      authorizeCreditLimit = true;
    }
  }
  const saleRequest = {
    customerId: customer?.id || "",
    items: cart.map((item) => ({
      productId: item.productId,
      ...(item.conditionalItemId ? { conditionalItemId: item.conditionalItemId } : {}),
      quantity: item.quantity,
      practicedUnitPrice: Number(item.practicedUnitPrice ?? item.unitPrice ?? 0),
      unitDiscount: Number(item.unitDiscount || 0),
      unitAddition: Number(item.unitAddition || 0),
    })),
    ...(pendingConditionalSaleDraft ? {
      conditionalId: pendingConditionalSaleDraft.conditionalId,
      conditionalReturnId: pendingConditionalSaleDraft.conditionalReturnId,
    } : {}),
    discount: readNumber(els.saleDiscount.value),
    addition: readNumber(els.saleAddition.value),
    payments,
    storeCreditInstallments: Math.max(1, Math.floor(readNumber(els.storeCreditInstallments.value))),
    storeCreditFirstDueDate: els.storeCreditFirstDueDate.value,
    authorizeCreditLimit,
  };

  if (!BACKEND_ENABLED) {
    showBackendRequiredMessage();
    return;
  }
  if (!pendingSaleKey) pendingSaleKey = createId();
  try {
    const response = await fetch("/api/sales", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Idempotency-Key": pendingSaleKey,
      },
      body: JSON.stringify(saleRequest),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      alert(payload.error || "Não foi possível finalizar a venda.");
      return;
    }
    applySaleResultLocally(payload.data);
    persistLocalOnly();
    showReceipt(payload.data.sale);
    clearSale();
    renderAll();
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para finalizar a venda. Tente novamente.");
  }
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
  mergeInventoryMovements(result.inventoryMovements || []);
  if (result.conditional) upsertConditional(result.conditional);
}

function clearSale() {
  cart = [];
  pendingSaleKey = "";
  pendingConditionalSaleDraft = null;
  els.saleCustomerSearch.value = "";
  els.saleDiscount.value = "0";
  els.saleAddition.value = "0";
  els.storeCreditInstallments.value = "1";
  els.storeCreditFirstDueDate.value = addCalendarMonthsIso(todayIso, 1);
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

async function openSaleReceiptPrint(sale) {
  const printWindow = prepareDocumentWindow();
  if (!printWindow) return;
  const generated = await generateOfficialDocument(
    "sale_receipt",
    sale.id,
    "thermal",
  );
  if (generated) openOfficialDocument(generated, true, printWindow);
  else printWindow.close();
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
  mergeInventoryMovements(result.inventoryMovements || []);
}

function setAfterSalesMode(mode) {
  if (!["return", "exchange", "warranty"].includes(mode)) return;
  afterSalesMode = mode;
  pendingAfterSalesKey = "";
  document.querySelectorAll("[data-after-sales-mode]").forEach((button) => {
    button.classList.toggle("active", button.dataset.afterSalesMode === mode);
  });
  els.exchangeReplacementCard.hidden = mode !== "exchange";
  els.warrantyDetailsCard.hidden = mode !== "warranty";
  els.returnReason.closest(".field").hidden = mode === "warranty";
  els.returnReason.required = mode !== "warranty";
  const currentReason = els.returnReason.value;
  const reasonOptions = mode === "exchange"
    ? ["", "Tamanho", "Cor", "Modelo", "Defeito", "Presente", "Outro"]
    : ["", "Desistência da compra", "Defeito no produto", "Produto incorreto", "Outro"];
  els.returnReason.innerHTML = reasonOptions
    .map((reason) => `<option value="${escapeHtml(reason)}">${escapeHtml(reason || "Selecione o motivo")}</option>`)
    .join("");
  els.returnReason.value = reasonOptions.includes(currentReason) ? currentReason : "";
  els.submitAfterSalesButton.textContent = mode === "exchange"
    ? "Registrar troca"
    : mode === "warranty"
      ? "Abrir garantia"
      : "Registrar devolução";
  els.returnTotalTitle.textContent = mode === "exchange"
    ? "Crédito dos itens"
    : mode === "warranty"
      ? "Valor histórico"
      : "Total da devolução";
  els.returnRefundTitle.textContent = mode === "exchange"
    ? "Diferença"
    : mode === "warranty"
      ? "Movimentação financeira"
      : "Valor a estornar";
  renderAfterSalesSelection();
  renderExchangeItems();
}

function scheduleAfterSalesLoad() {
  pendingAfterSalesKey = "";
  activeWarrantyId = "";
  clearTimeout(afterSalesLoadTimer);
  const sale = findSaleByCode(els.returnProductSearch.value);
  if (!sale) {
    afterSalesContext = null;
    renderAfterSalesSelection();
    return;
  }
  afterSalesLoadTimer = setTimeout(() => loadAfterSalesSale(sale.id), 180);
}

async function loadAfterSalesSale(saleId) {
  if (!saleId || !BACKEND_ENABLED) return;
  els.returnItemsList.className = "return-empty";
  els.returnItemsList.innerHTML = "<strong>Carregando itens da venda...</strong>";
  try {
    const response = await fetch(`/api/sales/${encodeURIComponent(saleId)}/after-sales`, { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      throw new Error(payload.error || "Não foi possível carregar o pós-venda.");
    }
    afterSalesContext = payload.data;
    renderAfterSalesSelection();
  } catch (error) {
    console.warn(error);
    afterSalesContext = null;
    els.returnItemsList.className = "return-empty";
    els.returnItemsList.innerHTML = `<strong>Não foi possível carregar a venda.</strong><small>${escapeHtml(error.message)}</small>`;
  }
}

function renderAfterSalesSelection() {
  if (!els.returnItemsList) return;
  const sale = findSaleByCode(els.returnProductSearch.value);
  if (!els.returnProductSearch.value.trim()) {
    els.returnItemsList.className = "return-empty";
    els.returnItemsList.innerHTML = "<strong>Nenhuma venda selecionada</strong><small>Busque uma venda para visualizar os itens.</small>";
    updateAfterSalesSummary();
    return;
  }
  if (!sale) {
    els.returnItemsList.className = "return-empty";
    els.returnItemsList.innerHTML = "<strong>Venda não encontrada</strong><small>Confira o número informado.</small>";
    updateAfterSalesSummary();
    return;
  }
  if (!afterSalesContext || afterSalesContext.sale?.id !== sale.id) {
    els.returnItemsList.className = "return-empty";
    els.returnItemsList.innerHTML = "<strong>Carregando saldo dos itens...</strong>";
    return;
  }
  const items = afterSalesContext.items || [];
  els.returnItemsList.className = items.length ? "return-items-list" : "return-empty";
  els.returnItemsList.innerHTML = items.length
    ? items.map((item, index) => `
      <div class="return-item-row" data-index="${index}">
        <span><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.barcode || "")}</small></span>
        <span>${escapeHtml([item.size, item.color].filter(Boolean).join(" / ") || "-")}</span>
        <span>${item.availableQuantity} de ${item.soldQuantity}</span>
        <label class="after-sales-check"><input class="after-sales-include" type="checkbox"${item.availableQuantity <= 0 ? " disabled" : ""}><span>Selecionar</span></label>
        <input class="return-qty" type="number" min="1" max="${item.availableQuantity}" step="1" value="1" disabled>
        <select class="return-condition" disabled><option value="resellable">Revenda</option><option value="damaged">Avariado</option></select>
        <b>${money.format(0)}</b>
      </div>
    `).join("")
    : "<strong>Nenhum item disponível.</strong><small>Os itens já foram devolvidos, trocados ou estão em garantia.</small>";
  els.returnItemsList.querySelectorAll("input, select").forEach((input) => {
    input.addEventListener("input", () => {
      pendingAfterSalesKey = "";
      const row = input.closest(".return-item-row");
      const checked = row.querySelector(".after-sales-include").checked;
      row.querySelector(".return-qty").disabled = !checked;
      row.querySelector(".return-condition").disabled = !checked || afterSalesMode === "warranty";
      if (afterSalesMode === "warranty" && checked) {
        els.returnItemsList.querySelectorAll(".after-sales-include").forEach((checkbox) => {
          if (checkbox !== row.querySelector(".after-sales-include")) checkbox.checked = false;
        });
        els.returnItemsList.querySelectorAll(".return-item-row").forEach((other) => {
          const selected = other.querySelector(".after-sales-include").checked;
          other.querySelector(".return-qty").disabled = !selected;
          other.querySelector(".return-condition").disabled = true;
        });
      }
      updateAfterSalesSummary();
    });
  });
  updateAfterSalesSummary();
}

function selectedAfterSalesItems() {
  if (!afterSalesContext) return [];
  return [...els.returnItemsList.querySelectorAll(".return-item-row")]
    .filter((row) => row.querySelector(".after-sales-include").checked)
    .map((row) => {
      const item = afterSalesContext.items[Number(row.dataset.index)];
      const quantity = Math.min(
        item.availableQuantity,
        Math.max(1, Math.floor(readNumber(row.querySelector(".return-qty").value))),
      );
      return {
        saleItemId: item.saleItemId,
        productId: item.productId,
        quantity,
        physicalCondition: row.querySelector(".return-condition").value,
        unitNet: Number(item.unitNet || 0),
      };
    });
}

function selectedAfterSalesCredit() {
  return round(selectedAfterSalesItems().reduce(
    (total, item) => total + item.quantity * item.unitNet,
    0,
  ));
}

function exchangeItemsTotal() {
  return round(exchangeItems.reduce(
    (total, item) => total + item.quantity * item.practicedUnitPrice,
    0,
  ));
}

function updateAfterSalesSummary() {
  const credit = selectedAfterSalesCredit();
  els.returnTotalLabel.textContent = money.format(credit);
  if (afterSalesMode === "exchange") {
    const difference = round(exchangeItemsTotal() - credit);
    els.returnRefundLabel.textContent = difference > 0
      ? `${money.format(difference)} a pagar`
      : difference < 0
        ? `${money.format(Math.abs(difference))} a devolver`
        : money.format(0);
    renderAfterSalesPaymentFields();
  } else if (afterSalesMode === "warranty") {
    els.returnRefundLabel.textContent = "Sem movimentação";
  } else {
    els.returnRefundLabel.textContent = money.format(credit);
  }
}

function findProductFromAfterSalesInput(value) {
  const query = normalize(value);
  if (!query) return null;
  const code = normalize(String(value).split(" - ", 1)[0]);
  return db.products.find((item) => normalize(item.barcode) === code)
    || db.products.find((item) => normalize(item.id) === query)
    || db.products.find((item) => normalize(item.name) === query)
    || db.products.find((item) => normalize(`${item.barcode} - ${item.name}`) === query);
}

function addExchangeProduct() {
  const product = findProductFromAfterSalesInput(els.exchangeProductSearch.value);
  if (!product) return alert("Produto substituto não encontrado.");
  const quantity = Math.max(1, Math.floor(readNumber(els.exchangeProductQuantity.value)));
  const practicedUnitPrice = els.exchangeProductPrice.value === ""
    ? Number(product.price || 0)
    : readNumber(els.exchangeProductPrice.value);
  const existing = exchangeItems.find((item) => item.productId === product.id);
  if (existing) {
    existing.quantity += quantity;
    existing.practicedUnitPrice = practicedUnitPrice;
  } else {
    exchangeItems.push({
      productId: product.id,
      name: product.name,
      barcode: product.barcode,
      quantity,
      practicedUnitPrice,
    });
  }
  els.exchangeProductSearch.value = "";
  els.exchangeProductQuantity.value = "1";
  els.exchangeProductPrice.value = "";
  pendingAfterSalesKey = "";
  renderExchangeItems();
}

function renderExchangeItems() {
  if (!els.exchangeItemsList) return;
  els.exchangeItemsList.className = exchangeItems.length
    ? "after-sales-compact-list"
    : "after-sales-compact-list empty";
  els.exchangeItemsList.innerHTML = exchangeItems.length
    ? exchangeItems.map((item, index) => `
      <div>
        <span><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.barcode)}</small></span>
        <span>${item.quantity} x ${money.format(item.practicedUnitPrice)}</span>
        <strong>${money.format(item.quantity * item.practicedUnitPrice)}</strong>
        <button class="danger" type="button" data-remove-exchange="${index}" aria-label="Remover">×</button>
      </div>
    `).join("")
    : "Nenhum produto substituto adicionado.";
  els.exchangeItemsList.querySelectorAll("[data-remove-exchange]").forEach((button) => {
    button.addEventListener("click", () => {
      exchangeItems.splice(Number(button.dataset.removeExchange), 1);
      pendingAfterSalesKey = "";
      renderExchangeItems();
    });
  });
  updateAfterSalesSummary();
}

function addExchangePaymentRow(method = "cash") {
  const difference = Math.max(0, round(exchangeItemsTotal() - selectedAfterSalesCredit()));
  const currentTotal = readExchangePayments().reduce((total, payment) => total + payment.amount, 0);
  const remaining = Math.max(0, round(difference - currentTotal));
  const row = document.createElement("div");
  row.className = "exchange-payment-row";
  row.innerHTML = `
    <label class="field">Forma<select class="exchange-pay-method">${salePaymentOptionsMarkup()}</select></label>
    <label class="field">Valor<input class="exchange-pay-amount" type="number" min="0.01" step="0.01" value="${fixed(remaining)}"></label>
    <label class="field exchange-pay-extra">Valor entregue<input class="exchange-pay-tendered" type="number" min="0" step="0.01" value="${fixed(remaining)}"></label>
    <button class="danger remove-exchange-payment" type="button" aria-label="Remover forma de pagamento">×</button>
  `;
  const select = row.querySelector(".exchange-pay-method");
  const directOption = [...select.options].find((option) => option.value === method);
  const cardOption = saleCardModalities.find((item) => item.method === method);
  select.value = directOption ? method : cardOption ? `card:${cardOption.cardModalityId}` : "cash";
  row.addEventListener("input", () => {
    pendingAfterSalesKey = "";
    updateExchangePaymentRow(row);
    renderExchangeStoreCreditFields();
  });
  row.querySelector(".remove-exchange-payment").addEventListener("click", () => {
    row.remove();
    pendingAfterSalesKey = "";
    renderExchangeStoreCreditFields();
  });
  els.exchangePaymentRows.append(row);
  updateExchangePaymentRow(row);
  renderExchangeStoreCreditFields();
}

function updateExchangePaymentRow(row) {
  const isCash = row.querySelector(".exchange-pay-method").value === "cash";
  row.querySelector(".exchange-pay-extra").hidden = !isCash;
}

function readExchangePayments() {
  if (!els.exchangePaymentRows) return [];
  const installments = Math.min(
    3,
    Math.max(1, Math.floor(readNumber(els.exchangeStoreCreditInstallments.value))),
  );
  return [...els.exchangePaymentRows.querySelectorAll(".exchange-payment-row")]
    .map((row) => {
      const selected = row.querySelector(".exchange-pay-method").value;
      const amount = round(readNumber(row.querySelector(".exchange-pay-amount").value));
      if (selected.startsWith("card:")) {
        const cardModalityId = selected.slice(5);
        const modality = saleCardModalities.find((item) => item.cardModalityId === cardModalityId);
        return {
          method: modality?.method || "",
          amount,
          cardModalityId,
          installments: Number(modality?.installments || 1),
        };
      }
      return {
        method: selected,
        amount,
        tenderedAmount: selected === "cash"
          ? readNumber(row.querySelector(".exchange-pay-tendered").value)
          : amount,
        installments: selected === "storeCredit" ? installments : 1,
      };
    })
    .filter((payment) => payment.amount > 0);
}

function renderExchangeStoreCreditFields() {
  const hasStoreCredit = readExchangePayments().some((payment) => payment.method === "storeCredit");
  els.exchangeStoreCreditFields.hidden = !hasStoreCredit;
  els.exchangeStoreCreditInstallments.required = hasStoreCredit;
  els.exchangeStoreCreditFirstDueDate.required = hasStoreCredit;
}

function renderAfterSalesPaymentFields() {
  if (!els.exchangePaymentFields) return;
  const difference = round(exchangeItemsTotal() - selectedAfterSalesCredit());
  els.exchangePaymentFields.hidden = difference <= 0;
  if (difference > 0 && !els.exchangePaymentRows.children.length) {
    addExchangePaymentRow();
  } else if (difference > 0 && els.exchangePaymentRows.children.length === 1) {
    const row = els.exchangePaymentRows.firstElementChild;
    row.querySelector(".exchange-pay-amount").value = fixed(difference);
    if (row.querySelector(".exchange-pay-method").value === "cash") {
      row.querySelector(".exchange-pay-tendered").value = fixed(difference);
    }
  }
  renderExchangeStoreCreditFields();
}

function nextAfterSalesKey() {
  if (!pendingAfterSalesKey) {
    pendingAfterSalesKey = `after-sales-${afterSalesMode}-${createId()}`;
  }
  return pendingAfterSalesKey;
}

async function uploadWarrantyEvidence() {
  const files = Array.from(els.warrantyPhotoFiles?.files || []);
  if (!files.length) return [];
  const saved = [];
  for (const file of files) {
    const formData = new FormData();
    formData.append("photo", file);
    const response = await fetch("/api/uploads/warranty-photo", {
      method: "POST",
      body: formData,
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) {
        throw new Error("Sessão expirada.");
      }
      throw new Error(payload.error || "Não foi possível enviar a foto da garantia.");
    }
    saved.push({
      url: payload.data.url,
      storage: payload.data.storage || "",
    });
  }
  return saved;
}

async function submitAfterSales(event) {
  event.preventDefault();
  const sale = findSaleByCode(els.returnProductSearch.value);
  const items = selectedAfterSalesItems();
  if (!sale || !afterSalesContext || afterSalesContext.sale?.id !== sale.id) {
    return alert("Selecione uma venda válida.");
  }
  if (!items.length) return alert("Selecione ao menos um item.");
  let endpoint = "/api/returns";
  let body;
  if (afterSalesMode === "return") {
    if (!els.returnReason.value) return alert("Informe o motivo da devolução.");
    body = {
      saleId: sale.id,
      reason: els.returnReason.value,
      notes: els.returnNotes.value.trim(),
      warrantyId: activeWarrantyId || "",
      items,
    };
  } else if (afterSalesMode === "exchange") {
    if (!els.returnReason.value) return alert("Informe o motivo da troca.");
    if (!exchangeItems.length) return alert("Adicione o produto substituto.");
    const difference = round(exchangeItemsTotal() - selectedAfterSalesCredit());
    const payments = difference > 0 ? readExchangePayments() : [];
    const paymentTotal = round(payments.reduce((total, payment) => total + payment.amount, 0));
    if (difference > 0 && Math.abs(paymentTotal - difference) > 0.01) {
      return alert("A soma das formas de pagamento deve ser igual à diferença da troca.");
    }
    if (payments.some((payment) => ["debit", "credit"].includes(payment.method) && !payment.cardModalityId)) {
      return alert("Selecione a modalidade de cartão.");
    }
    if (payments.some((payment) => payment.method === "cash" && payment.tenderedAmount < payment.amount)) {
      return alert("O valor entregue em dinheiro não pode ser menor que o valor informado.");
    }
    endpoint = "/api/exchanges";
    body = {
      saleId: sale.id,
      reason: els.returnReason.value,
      notes: els.returnNotes.value.trim(),
      warrantyId: activeWarrantyId || "",
      returnedItems: items,
      newItems: exchangeItems.map((item) => ({
        productId: item.productId,
        quantity: item.quantity,
        practicedUnitPrice: item.practicedUnitPrice,
      })),
      payments,
      storeCreditInstallments: Math.min(
        3,
        Math.max(1, Math.floor(readNumber(els.exchangeStoreCreditInstallments.value))),
      ),
      storeCreditFirstDueDate: els.exchangeStoreCreditFirstDueDate.value,
    };
  } else {
    if (items.length !== 1) return alert("A garantia deve ser aberta para um item por vez.");
    const defectDescription = els.warrantyDefectDescription.value.trim();
    if (!els.warrantyDefectCategory.value || !defectDescription) {
      return alert("Informe a categoria e a descrição do defeito.");
    }
    const externalPhotos = els.warrantyPhotoUrls.value.split(/\r?\n/)
      .map((value) => value.trim())
      .filter(Boolean)
      .map((url) => ({ url }));
    const photos = externalPhotos;
    if (photos.length > 5) return alert("Informe no máximo 5 fotos.");
    const fileCount = els.warrantyPhotoFiles?.files?.length || 0;
    if (photos.length + fileCount > 5) return alert("Informe no máximo 5 fotos.");
    photos.push(...await uploadWarrantyEvidence());
    endpoint = "/api/warranties";
    body = {
      saleId: sale.id,
      saleItemId: items[0].saleItemId,
      quantity: items[0].quantity,
      defectCategory: els.warrantyDefectCategory.value,
      defectDescription,
      physicalLocation: els.warrantyPhysicalLocation.value,
      contactName: els.warrantyContactName.value.trim(),
      contactPhone: els.warrantyContactPhone.value.trim(),
      photos,
    };
  }
  els.submitAfterSalesButton.disabled = true;
  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Idempotency-Key": nextAfterSalesKey(),
      },
      body: JSON.stringify(body),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      throw new Error(payload.error || "Não foi possível registrar o atendimento.");
    }
    await syncFromServer();
    clearAfterSalesForm();
  } catch (error) {
    console.warn(error);
    alert(error.message || "Não foi possível registrar o atendimento.");
  } finally {
    els.submitAfterSalesButton.disabled = false;
  }
}

function clearAfterSalesForm() {
  els.returnForm.reset();
  afterSalesContext = null;
  exchangeItems = [];
  els.exchangePaymentRows.innerHTML = "";
  els.exchangeStoreCreditInstallments.value = "1";
  els.exchangeStoreCreditFirstDueDate.value = addCalendarMonthsIso(todayIso, 1);
  pendingAfterSalesKey = "";
  activeWarrantyId = "";
  setAfterSalesMode("return");
  renderAfterSalesSelection();
}

function warrantyActionsMarkup(warranty) {
  const options = [];
  if (warranty.physicalLocation === "customer" && !["resolved", "cancelled"].includes(warranty.status)) {
    options.push('<option value="receive_at_store">Receber na loja</option>');
  }
  if (warranty.status === "open") options.push('<option value="start_analysis">Iniciar análise</option>');
  if (["open", "analysis"].includes(warranty.status) && warranty.physicalLocation === "store") {
    options.push('<option value="send_supplier">Enviar ao fornecedor</option>');
  }
  if (["open", "analysis", "supplier"].includes(warranty.status)) {
    options.push('<option value="approve">Aprovar</option><option value="reject">Rejeitar</option>');
  }
  if (warranty.status === "approved") {
    options.push('<option value="resolve_repair">Registrar reparo</option><option value="resolve_substitution">Registrar substituição</option>');
  }
  if (warranty.status === "rejected" && warranty.physicalLocation === "customer") {
    options.push('<option value="close_rejection">Concluir recusa</option>');
  }
  if (warranty.awaitingCustomerDelivery) options.push('<option value="deliver_customer">Entregar ao cliente</option>');
  if (!["resolved", "cancelled"].includes(warranty.status) && isAdmin()) options.push('<option value="cancel">Cancelar</option>');
  return options.join("");
}

function renderAfterSalesHistory() {
  if (!els.afterSalesHistoryList) return;
  const entries = [
    ...(db.returns || []).map((item) => ({ ...item, kind: "Devolução", sortAt: item.createdAt })),
    ...(db.exchanges || []).map((item) => ({ ...item, kind: "Troca", sortAt: item.createdAt })),
    ...(db.warranties || []).map((item) => ({ ...item, kind: "Garantia", sortAt: item.createdAt })),
  ].sort((a, b) => String(b.sortAt || "").localeCompare(String(a.sortAt || "")));
  els.afterSalesHistoryList.className = entries.length ? "table-list" : "table-list empty";
  els.afterSalesHistoryList.innerHTML = entries.length
    ? entries.map((item) => {
      const number = item.returnNumber
        ? `DEV${String(item.returnNumber).padStart(4, "0")}`
        : item.exchangeNumber
          ? `TROCA${String(item.exchangeNumber).padStart(4, "0")}`
          : item.warrantyNumber
            ? `GAR${String(item.warrantyNumber).padStart(4, "0")}`
            : item.id;
      const value = item.netTotal ?? item.differenceAmount ?? 0;
      const actions = item.kind === "Garantia" ? warrantyActionsMarkup(item) : "";
      const exchangeCancellation = (
        item.kind === "Troca" && item.status === "completed"
      )
        ? `<button class="danger" type="button" data-cancel-exchange="${escapeHtml(item.id)}">Cancelar troca</button>`
        : "";
      const exchangeActions = item.kind === "Troca"
        ? `<div class="after-sales-history-action"><button class="ghost" type="button" data-print-exchange="${escapeHtml(item.id)}">Imprimir</button>${exchangeCancellation}</div>`
        : "";
      return `
        <div class="after-sales-history-row">
          <span><strong>${escapeHtml(number)}</strong><small>${escapeHtml(item.kind)} · ${formatDateTime(item.createdAt)}</small></span>
          <span>${escapeHtml(item.customerName || "-")}</span>
          <span>${escapeHtml(item.productName || item.reason || item.status || "-")}</span>
          <strong>${item.kind === "Garantia" ? escapeHtml(item.status) : money.format(value)}</strong>
          ${actions ? `<div class="after-sales-history-action"><select data-warranty-action="${escapeHtml(item.id)}">${actions}</select><button class="ghost" type="button" data-run-warranty="${escapeHtml(item.id)}">Executar</button></div>` : exchangeActions || "<span></span>"}
          ${item.kind === "Garantia" && item.status === "approved" ? `<div class="warranty-solution-actions"><button class="ghost" type="button" data-warranty-return="${escapeHtml(item.id)}">Devolver</button><button class="ghost" type="button" data-warranty-exchange="${escapeHtml(item.id)}">Trocar</button></div>` : ""}
        </div>
      `;
    }).join("")
    : "Nenhum atendimento registrado.";
  els.afterSalesHistoryList.querySelectorAll("[data-run-warranty]").forEach((button) => {
    button.addEventListener("click", () => executeWarrantyAction(button.dataset.runWarranty));
  });
  els.afterSalesHistoryList.querySelectorAll("[data-warranty-return]").forEach((button) => {
    button.addEventListener("click", () => startWarrantySolution(button.dataset.warrantyReturn, "return"));
  });
  els.afterSalesHistoryList.querySelectorAll("[data-warranty-exchange]").forEach((button) => {
    button.addEventListener("click", () => startWarrantySolution(button.dataset.warrantyExchange, "exchange"));
  });
  els.afterSalesHistoryList.querySelectorAll("[data-cancel-exchange]").forEach((button) => {
    button.addEventListener("click", () => cancelExchange(button.dataset.cancelExchange));
  });
  els.afterSalesHistoryList.querySelectorAll("[data-print-exchange]").forEach((button) => {
    button.addEventListener("click", () => printExchangeDocument(button.dataset.printExchange));
  });
}

async function printExchangeDocument(exchangeId) {
  const printWindow = prepareDocumentWindow();
  if (!printWindow) return;
  const generated = await generateOfficialDocument(
    "exchange",
    exchangeId,
    "a4",
  );
  if (generated) openOfficialDocument(generated, true, printWindow);
  else printWindow.close();
}

async function cancelExchange(exchangeId) {
  const reason = prompt("Informe o motivo do cancelamento da troca:")?.trim();
  if (!reason) return;
  if (!confirm("Confirma o cancelamento formal desta troca?")) return;
  try {
    const response = await fetch(`/api/exchanges/${encodeURIComponent(exchangeId)}/cancel`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Idempotency-Key": `exchange-cancel-${exchangeId}-${createId()}`,
      },
      body: JSON.stringify({ reason }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.error || "Não foi possível cancelar a troca.");
    }
    await syncFromServer();
  } catch (error) {
    alert(error.message);
  }
}

async function executeWarrantyAction(warrantyId) {
  const select = els.afterSalesHistoryList.querySelector(`[data-warranty-action="${CSS.escape(warrantyId)}"]`);
  const action = select?.value;
  if (!action) return;
  const body = { action };
  if (action === "send_supplier") {
    const supplierInput = prompt("Informe o nome ou código do fornecedor:");
    const supplier = db.suppliers.find((item) => normalize(item.id) === normalize(supplierInput))
      || db.suppliers.find((item) => normalize(item.name) === normalize(supplierInput));
    if (!supplier) return alert("Fornecedor ativo não encontrado.");
    body.supplierId = supplier.id;
    body.protocol = prompt("Protocolo do fornecedor (opcional):") || "";
  }
  if (["reject", "cancel", "resolve_repair", "resolve_substitution"].includes(action)) {
    body.notes = prompt("Informe o motivo ou a solução aplicada:") || "";
    if (!body.notes) return;
  }
  if (["resolve_repair", "resolve_substitution"].includes(action)) {
    body.awaitingCustomerDelivery = confirm("O produto ficará aguardando retirada pelo cliente?");
  }
  if (action === "resolve_substitution") {
    const destination = normalize(
      prompt("Destino do produto substituto: CLIENTE ou ESTOQUE", "CLIENTE") || "",
    );
    if (!["cliente", "estoque"].includes(destination)) {
      return alert("Informe CLIENTE ou ESTOQUE.");
    }
    const productInput = prompt("Informe o codigo ou nome do produto substituto:") || "";
    const product = db.products.find((item) => normalize(item.id) === normalize(productInput))
      || db.products.find((item) => normalize(item.barcode) === normalize(productInput))
      || db.products.find((item) => normalize(item.name) === normalize(productInput));
    if (!product) return alert("Produto substituto nao encontrado.");
    const quantity = Math.floor(readNumber(prompt("Quantidade recebida:", "1")));
    if (quantity <= 0) return alert("Informe uma quantidade valida.");
    body.replacementDestination = destination === "estoque" ? "stock" : "customer";
    body.replacementProductId = product.id;
    body.replacementQuantity = quantity;
    if (body.replacementDestination === "stock") {
      const unitCost = readNumber(
        prompt("Confirme o custo unitario da entrada:", fixed(product.cost)),
      );
      if (unitCost <= 0) return alert("Informe um custo unitario valido.");
      body.replacementUnitCost = unitCost;
      body.awaitingCustomerDelivery = false;
    }
  }
  try {
    const response = await fetch(`/api/warranties/${encodeURIComponent(warrantyId)}/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.error || "Não foi possível atualizar a garantia.");
    await syncFromServer();
  } catch (error) {
    alert(error.message);
  }
}

function startWarrantySolution(warrantyId, mode) {
  const warranty = (db.warranties || []).find((item) => item.id === warrantyId);
  if (!warranty) return;
  activeWarrantyId = warrantyId;
  setAfterSalesMode(mode);
  els.returnProductSearch.value = warranty.saleId;
  loadAfterSalesSale(warranty.saleId);
  window.scrollTo({ top: els.returnForm.getBoundingClientRect().top + window.scrollY - 20, behavior: "smooth" });
}

function findSaleByCode(value) {
  const query = normalize(value);
  if (!query) return null;
  return db.sales.find((sale) => normalize(sale.id) === query) || db.sales.find((sale) => normalize(sale.id).startsWith(query));
}

function renderSaleHistory() {
  if (!els.saleHistoryList || !els.saleHistoryDetailPanel) return;
  const sales = filteredSaleHistory();
  const activeSales = sales.filter((sale) => sale.status !== "cancelled");
  const revenue = activeSales.reduce((total, sale) => total + Number(sale.total || 0), 0);
  const average = activeSales.length ? revenue / activeSales.length : 0;
  els.saleHistoryTotalCount.textContent = String(sales.length);
  els.saleHistoryRevenue.textContent = money.format(revenue);
  els.saleHistoryAverage.textContent = money.format(average);
  els.saleHistoryResultCount.textContent = `${sales.length} venda${sales.length === 1 ? "" : "s"} encontrada${sales.length === 1 ? "" : "s"}`;
  if (!sales.some((sale) => sale.id === selectedSaleHistoryKey)) selectedSaleHistoryKey = sales[0]?.id || "";
  els.saleHistoryList.innerHTML = "";
  if (!sales.length) {
    els.saleHistoryList.innerHTML = `<tr><td colspan="8" class="empty-cell">Nenhuma venda encontrada.</td></tr>`;
    els.saleHistoryFooter.textContent = "Mostrando 0 vendas";
    renderSaleHistorySide(null);
    return;
  }
  sales.forEach((sale) => {
    const row = document.createElement("tr");
    row.className = sale.id === selectedSaleHistoryKey ? "selected" : "";
    row.innerHTML = `
      <td><strong>${escapeHtml(sale.id)}</strong></td>
      <td>${formatDateTime(sale.createdAt)}</td>
      <td>${escapeHtml(sale.customerName || "Venda simples")}</td>
      <td>${saleItemCount(sale)}</td>
      <td>${money.format(sale.total || 0)}</td>
      <td>${escapeHtml(salePaymentSummary(sale))}</td>
      <td><span class="sale-history-status ${sale.status === "cancelled" ? "cancelled" : "completed"}">${sale.status === "cancelled" ? "Cancelada" : "Finalizada"}</span></td>
      <td><div class="sale-history-row-actions"></div></td>
    `;
    row.addEventListener("click", () => {
      selectedSaleHistoryKey = sale.id;
      renderSaleHistory();
    });
    row.querySelector(".sale-history-row-actions").append(button("Ver", "icon-button", (event) => {
      event.stopPropagation();
      selectedSaleHistoryKey = sale.id;
      renderSaleHistory();
    }));
    els.saleHistoryList.append(row);
  });
  els.saleHistoryFooter.innerHTML = `
    <span>Mostrando 1 a ${sales.length} de ${sales.length} venda${sales.length === 1 ? "" : "s"}</span>
    <div class="credit-pagination"><button type="button" disabled>Anterior</button><button type="button" class="active">1</button><button type="button" disabled>Próximo</button></div>
  `;
  renderSaleHistorySide(sales.find((sale) => sale.id === selectedSaleHistoryKey));
}

function updateSaleHistoryPeriodInputs() {
  const period = els.saleHistoryPeriod.value;
  if (period === "today") {
    els.saleHistoryStart.value = todayIso;
    els.saleHistoryEnd.value = todayIso;
  } else if (period === "month") {
    const now = new Date();
    els.saleHistoryStart.value = toDateInput(new Date(now.getFullYear(), now.getMonth(), 1));
    els.saleHistoryEnd.value = todayIso;
  }
}

function filteredSaleHistory() {
  const query = normalize(els.saleHistorySearch.value || "");
  const type = els.saleHistoryType.value || "name";
  const period = els.saleHistoryPeriod.value || "all";
  const status = els.saleHistoryStatus.value || "all";
  const start = els.saleHistoryStart.value || "0000-01-01";
  const end = els.saleHistoryEnd.value || "9999-12-31";
  return db.sales.slice()
    .filter((sale) => status === "all" || (status === "cancelled" ? sale.status === "cancelled" : sale.status !== "cancelled"))
    .filter((sale) => period === "all" || (String(sale.createdAt || "").slice(0, 10) >= start && String(sale.createdAt || "").slice(0, 10) <= end))
    .filter((sale) => saleHistoryMatchesSearch(sale, type, query))
    .sort((a, b) => String(b.createdAt || "").localeCompare(String(a.createdAt || "")));
}

function saleHistoryMatchesSearch(sale, type, query) {
  if (!query) return true;
  const customer = db.customers.find((item) => item.id === sale.customerId) || {};
  if (type === "sale") return normalize(sale.id).includes(query);
  if (type === "cpf") return normalize(customer.cpf || "").includes(query);
  if (type === "phone") return normalize([customer.whatsapp, customer.phone].join(" ")).includes(query);
  if (type === "barcode") return (sale.items || []).some((item) => normalize(item.barcode || "").includes(query));
  return normalize([sale.customerName, customer.name].join(" ")).includes(query);
}

function saleItemCount(sale) {
  return (sale.items || []).reduce((total, item) => total + Number(item.quantity || 0), 0);
}

function salePaymentSummary(sale) {
  const parts = (sale.payments || []).map((payment) => paymentLabels[payment.method] || payment.method).filter(Boolean);
  return parts.length ? [...new Set(parts)].join(", ") : "-";
}

function renderSaleHistorySide(sale) {
  if (!sale) {
    els.saleHistoryDetailPanel.className = "panel sale-history-side-panel empty";
    els.saleHistoryDetailPanel.textContent = "Selecione uma venda para visualizar os detalhes.";
    return;
  }
  els.saleHistoryDetailPanel.className = "panel sale-history-side-panel";
  const customer = db.customers.find((item) => item.id === sale.customerId) || {};
  const receivables = db.receivables.filter((item) => item.saleId === sale.id);
  const items = (sale.items || []).map((item) => `
    <div><span>${escapeHtml(item.quantity || 0)}x ${escapeHtml(item.name || "-")}</span><strong>${money.format(item.total || 0)}</strong></div>
  `).join("") || `<p class="empty">Sem itens.</p>`;
  const payments = (sale.payments || []).map((payment) => `
    <div><span>${escapeHtml(paymentLabels[payment.method] || payment.method || "-")}</span><strong>${money.format(payment.amount || 0)}</strong></div>
  `).join("") || `<p class="empty">Sem pagamentos.</p>`;
  const receivablePayments = receivables.flatMap((item) => receivablePaymentRows(item).map((payment) => `
    <div><span>${formatDateTime(payment.createdAt)} - ${escapeHtml(paymentLabels[payment.method] || payment.method || "-")}</span><strong>${money.format(payment.amount || 0)}</strong></div>
  `)).join("");
  els.saleHistoryDetailPanel.innerHTML = `
    <div class="sale-history-side-head">
      <div><h3>Venda ${escapeHtml(sale.id)}</h3><small>${sale.status === "cancelled" ? "Cancelada" : "Finalizada"}</small></div>
      <button class="modal-close" type="button" aria-label="Limpar seleção">×</button>
    </div>
    <div class="sale-history-customer">
      <span>${escapeHtml(initialsFromName(sale.customerName || "VS"))}</span>
      <div><strong>${escapeHtml(sale.customerName || "Venda simples")}</strong><small>${escapeHtml(customer.whatsapp || customer.phone || "")}</small></div>
    </div>
    <div class="sale-history-side-meta">
      <p>Data: <strong>${formatDateTime(sale.createdAt)}</strong></p>
      <p>Itens: <strong>${saleItemCount(sale)}</strong></p>
    </div>
    <section><h4>Produtos</h4>${items}</section>
    <section><h4>Pagamento</h4>${payments}${receivablePayments ? `<h4>Baixas do crediário</h4>${receivablePayments}` : ""}</section>
    <div class="sale-history-side-total">
      <span>Total</span><strong>${money.format(sale.total || 0)}</strong>
    </div>
    <div class="sale-history-side-actions">
      <button class="ghost sale-history-print" type="button">Reimprimir</button>
      <button class="ghost sale-history-return" type="button">Troca/Devolução</button>
      <button class="danger sale-history-cancel" type="button"${sale.status === "cancelled" ? " disabled" : ""}>Cancelar venda</button>
    </div>
  `;
  els.saleHistoryDetailPanel.querySelector(".modal-close").addEventListener("click", () => {
    selectedSaleHistoryKey = "";
    renderSaleHistory();
  });
  els.saleHistoryDetailPanel.querySelector(".sale-history-print").addEventListener("click", () => openSaleReceiptPrint(sale));
  els.saleHistoryDetailPanel.querySelector(".sale-history-return").addEventListener("click", () => {
    activateSubtab("devolucao");
    els.returnProductSearch.value = sale.id;
    loadAfterSalesSale(sale.id);
  });
  els.saleHistoryDetailPanel.querySelector(".sale-history-cancel").addEventListener("click", () => cancelSale(sale.id));
}

function exportSaleHistory() {
  const rows = filteredSaleHistory();
  const csv = ["venda,data,cliente,itens,total,pagamento,status", ...rows.map((sale) => [
    sale.id,
    formatDateTime(sale.createdAt),
    sale.customerName || "Venda simples",
    saleItemCount(sale),
    fixed(sale.total || 0),
    salePaymentSummary(sale),
    sale.status === "cancelled" ? "Cancelada" : "Finalizada",
  ].map((value) => `"${String(value).replaceAll('"', '""')}"`).join(","))].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `historico-vendas-${todayIso}.csv`;
  link.click();
  URL.revokeObjectURL(url);
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
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": createId(),
        },
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
  if (!sale || !confirm("Cancelar venda e devolver os itens ao estoque?")) return;
  const reason = prompt("Informe o motivo do cancelamento:");
  if (!reason?.trim()) return;
  if (BACKEND_ENABLED) {
    try {
      const response = await fetch(`/api/sales/${encodeURIComponent(saleId)}/cancel`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": createId(),
        },
        body: JSON.stringify({ reason: reason.trim() }),
      });
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
  mergeInventoryMovements(result.inventoryMovements || []);
}

function renderCreditCustomersLegacy() {
  const query = normalize(els.creditCustomerSearch.value);
  const customers = db.customers.filter((customer) => {
    const text = [customer.name, customer.whatsapp, customer.phone, customer.cpf].join(" ");
    return customerCreditStats(customer.id).open > 0 && (!query || normalize(text).includes(query));
  });
  const customerIds = new Set(customers.map((customer) => customer.id));
  const creditItems = db.receivables.filter((item) => item.method === "storeCredit" && item.status !== "cancelled" && receivableBalance(item) > 0 && customerIds.has(item.customerId));
  const openTotal = creditItems.reduce((total, item) => total + receivableBalance(item), 0);
  const dueItems = creditItems.filter((item) => item.dueDate >= todayIso);
  const overdueItems = creditItems.filter((item) => item.dueDate < todayIso);
  els.creditOpenTotal.textContent = money.format(openTotal);
  els.creditOpenCount.textContent = `${creditItems.length} parcela${creditItems.length === 1 ? "" : "s"}`;
  els.creditDueTotal.textContent = money.format(dueItems.reduce((total, item) => total + receivableBalance(item), 0));
  els.creditDueCount.textContent = `${dueItems.length} parcela${dueItems.length === 1 ? "" : "s"}`;
  els.creditOverdueTotal.textContent = money.format(overdueItems.reduce((total, item) => total + receivableBalance(item), 0));
  els.creditOverdueCount.textContent = `${overdueItems.length} parcela${overdueItems.length === 1 ? "" : "s"}`;
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

function renderCreditCustomers() {
  const query = normalize(els.creditCustomerSearch.value);
  const searchedCustomers = db.customers.filter((customer) => {
    const stats = customerCreditStats(customer.id);
    const text = [customer.name, customer.whatsapp, customer.phone, customer.cpf].join(" ");
    return stats.totalCount > 0 && (!query || normalize(text).includes(query));
  });
  const countByStatus = {
    all: searchedCustomers.length,
    ok: searchedCustomers.filter((customer) => creditStatusFromStats(customerCreditStats(customer.id)) === "ok").length,
    overdue: searchedCustomers.filter((customer) => creditStatusFromStats(customerCreditStats(customer.id)) === "overdue").length,
    paid: searchedCustomers.filter((customer) => creditStatusFromStats(customerCreditStats(customer.id)) === "paid").length,
  };
  const customers = searchedCustomers.filter((customer) => creditFilterStatus === "all" || creditStatusFromStats(customerCreditStats(customer.id)) === creditFilterStatus);
  const customerIds = new Set(customers.map((customer) => customer.id));
  const creditItems = db.receivables.filter((item) => item.method === "storeCredit" && item.status !== "cancelled" && customerIds.has(item.customerId));
  const openItems = creditItems.filter((item) => receivableBalance(item) > 0);
  const openTotal = openItems.reduce((total, item) => total + receivableBalance(item), 0);
  const dueItems = openItems.filter((item) => item.dueDate >= todayIso);
  const overdueItems = openItems.filter((item) => item.dueDate < todayIso);
  els.creditOpenTotal.textContent = money.format(openTotal);
  els.creditOpenCount.textContent = `${openItems.length} parcela${openItems.length === 1 ? "" : "s"}`;
  els.creditDueTotal.textContent = money.format(dueItems.reduce((total, item) => total + receivableBalance(item), 0));
  els.creditDueCount.textContent = `${dueItems.length} parcela${dueItems.length === 1 ? "" : "s"}`;
  els.creditOverdueTotal.textContent = money.format(overdueItems.reduce((total, item) => total + receivableBalance(item), 0));
  els.creditOverdueCount.textContent = `${overdueItems.length} parcela${overdueItems.length === 1 ? "" : "s"}`;
  if (els.creditFilterAllCount) els.creditFilterAllCount.textContent = countByStatus.all;
  if (els.creditFilterOkCount) els.creditFilterOkCount.textContent = countByStatus.ok;
  if (els.creditFilterOverdueCount) els.creditFilterOverdueCount.textContent = countByStatus.overdue;
  if (els.creditFilterPaidCount) els.creditFilterPaidCount.textContent = countByStatus.paid;
  document.querySelectorAll("[data-credit-filter]").forEach((button) => button.classList.toggle("active", button.dataset.creditFilter === creditFilterStatus));
  els.creditCustomerList.innerHTML = "";
  els.creditFooter.innerHTML = "";
  if (!customers.length) {
    els.creditCustomerList.innerHTML = `<tr><td colspan="6" class="empty-cell">Nenhum cliente encontrado.</td></tr>`;
    els.creditFooter.textContent = "Mostrando 0 clientes";
    renderCreditCustomerDetail(null);
    return;
  }
  if (!customers.some((customer) => customer.id === selectedCreditCustomerId)) selectedCreditCustomerId = customers[0].id;
  customers.forEach((customer) => {
    const stats = customerCreditStats(customer.id);
    const statusKey = creditStatusFromStats(stats);
    const row = document.createElement("tr");
    row.className = customer.id === selectedCreditCustomerId ? "selected" : "";
    row.innerHTML = `
      <td>
        <div class="credit-client-cell">
          <span>${escapeHtml(initialsFromName(customer.name || "CL"))}</span>
          <div><strong>${escapeHtml(customer.name)}</strong><small>${escapeHtml(customer.whatsapp || "-")} | CPF: ${escapeHtml(customer.cpf || "-")}</small></div>
        </div>
      </td>
      <td>${money.format(customerLimit(customer))}</td>
      <td class="${stats.overdueCount > 0 ? "value-bad" : stats.open > 0 ? "value-ok" : ""}">${money.format(stats.open)}</td>
      <td><strong>${stats.openCount}</strong><small>${stats.totalCount} no histórico</small></td>
      <td><span class="credit-status ${statusKey === "overdue" ? "overdue" : statusKey === "paid" ? "paid" : "ok"}">${creditStatusLabel(statusKey)}</span></td>
      <td><div class="credit-actions"></div></td>
    `;
    row.addEventListener("click", () => {
      selectedCreditCustomerId = customer.id;
      renderCreditCustomers();
    });
    row.querySelector(".credit-actions").append(button("⋮", "credit-menu-button", () => {
      selectedCreditCustomerId = customer.id;
      renderCreditCustomers();
    }));
    els.creditCustomerList.append(row);
  });
  els.creditFooter.innerHTML = `
    <span>Mostrando 1 a ${customers.length} de ${searchedCustomers.length} cliente${searchedCustomers.length === 1 ? "" : "s"}</span>
    <div class="credit-pagination"><button type="button" disabled>Anterior</button><button type="button" class="active">1</button><button type="button" disabled>Próximo</button></div>
  `;
  renderCreditCustomerDetail(db.customers.find((customer) => customer.id === selectedCreditCustomerId));
}

function renderCreditCustomerDetail(customer) {
  if (!els.creditCustomerDetail) return;
  if (!customer) {
    els.creditCustomerDetail.className = "panel credit-detail-panel empty";
    els.creditCustomerDetail.textContent = "Selecione um cliente para visualizar o resumo.";
    return;
  }
  const stats = customerCreditStats(customer.id);
  const statusKey = creditStatusFromStats(stats);
  const nextDue = stats.openItems.slice().sort((a, b) => String(a.dueDate || "").localeCompare(String(b.dueDate || "")))[0]?.dueDate || "";
  const accountHistory = stats.items
    .slice()
    .sort((a, b) => String(a.dueDate || "").localeCompare(String(b.dueDate || "")))
    .map((item) => `
      <article class="credit-account-history">
        <div>
          <strong>Venda ${escapeHtml(item.saleId || "-")} · Parcela ${escapeHtml(item.installment || "-")}</strong>
          <small>Original ${money.format(item.amount || 0)} · Pago ${money.format(item.received || 0)} · Saldo ${money.format(receivableBalance(item))}</small>
          <small>Vencimento original ${formatDate(item.originalDueDate || item.dueDate)} · Atual ${formatDate(item.dueDate)}</small>
        </div>
        <div class="credit-account-actions">
          ${receivableBalance(item) > 0 ? `<button class="ghost" type="button" data-credit-renegotiate="${escapeHtml(item.id)}">Renegociar</button>` : ""}
        </div>
        ${(item.payments || []).length ? `
          <details>
            <summary>${item.payments.length} pagamento${item.payments.length === 1 ? "" : "s"}</summary>
            ${(item.payments || []).map((payment) => `
              <p>${formatDateTime(payment.createdAt)} · ${escapeHtml(paymentLabels[payment.method] || payment.method || "-")} · Recebido ${money.format(payment.amount || 0)}${Number(payment.discountAmount || 0) ? ` · Desconto ${money.format(payment.discountAmount)}` : ""}${Number(payment.interestAmount || 0) ? ` · Juros ${money.format(payment.interestAmount)}` : ""}${Number(payment.fineAmount || 0) ? ` · Multa ${money.format(payment.fineAmount)}` : ""}</p>
            `).join("")}
          </details>
        ` : ""}
        ${(item.renegotiations || []).length ? `
          <details>
            <summary>${item.renegotiations.length} renegociação${item.renegotiations.length === 1 ? "" : "ões"}</summary>
            ${(item.renegotiations || []).map((entry) => `
              <p>${formatDateTime(entry.createdAt)} · ${formatDate(entry.previousDueDate)} para ${formatDate(entry.newDueDate)} · Saldo ${money.format(entry.previousOpenAmount)} para ${money.format(entry.newOpenAmount)} · ${escapeHtml(entry.userName || "-")}</p>
            `).join("")}
          </details>
        ` : ""}
      </article>
    `).join("");
  els.creditCustomerDetail.className = "panel credit-detail-panel";
  els.creditCustomerDetail.innerHTML = `
    <div class="credit-detail-head">
      <span>${escapeHtml(initialsFromName(customer.name || "CL"))}</span>
      <div><strong>${escapeHtml(customer.name || "-")}</strong><small>${escapeHtml(customer.whatsapp || customer.phone || "-")}</small><em>Cliente desde ${formatDate(customer.createdAt || customer.updatedAt || todayIso)}</em></div>
      <b class="credit-status ${statusKey === "overdue" ? "overdue" : statusKey === "paid" ? "paid" : "ok"}">${creditStatusLabel(statusKey)}</b>
    </div>
    <div class="credit-detail-list">
      <div><span>Limite de crédito</span><strong>${money.format(customerLimit(customer))}</strong></div>
      <div><span>Saldo devedor</span><strong class="${stats.open > 0 ? "value-bad" : ""}">${money.format(stats.open)}</strong></div>
      <div><span>Parcelas em aberto</span><strong>${stats.openCount}</strong></div>
      <div><span>Próximo vencimento</span><strong>${nextDue ? formatDate(nextDue) : "-"}</strong></div>
    </div>
    <div id="creditCustomerScore">${renderCustomerScoreCard(customerScoreCache.get(customer.id))}</div>
    <section class="credit-detail-summary">
      <h3>Resumo por situação</h3>
      <div><span><i class="dot green"></i>Em dia</span><strong>${money.format(stats.due)}</strong><small>${stats.dueCount} parcelas</small></div>
      <div><span><i class="dot red"></i>Atrasadas</span><strong>${money.format(stats.overdue)}</strong><small>${stats.overdueCount} parcelas</small></div>
      <div><span><i class="dot gray"></i>Quitadas</span><strong>${money.format(stats.paid)}</strong><small>${stats.paidCount} parcelas</small></div>
    </section>
    <section class="credit-account-history-list">
      <h3>Parcelas e histórico</h3>
      ${accountHistory || "<p>Nenhuma parcela registrada.</p>"}
    </section>
    <div class="credit-detail-actions">
      <button class="primary" type="button" id="creditDetailReceiveButton"${stats.open <= 0 ? " disabled" : ""}>Registrar pagamento</button>
      <button class="ghost" type="button" id="creditDetailEditButton">Editar cliente</button>
    </div>
  `;
  els.creditCustomerDetail.querySelector("#creditDetailReceiveButton").addEventListener("click", () => openCreditReceiveModal(customer.id));
  els.creditCustomerDetail.querySelector("#creditDetailEditButton").addEventListener("click", () => editCustomer(customer.id));
  els.creditCustomerDetail.querySelectorAll("[data-credit-renegotiate]").forEach((buttonElement) => {
    buttonElement.addEventListener("click", () => openCreditRenegotiation(buttonElement.dataset.creditRenegotiate));
  });
  loadCustomerScore(customer.id, els.creditCustomerDetail.querySelector("#creditCustomerScore"));
}

async function loadCustomerScore(customerId, target) {
  if (!customerId || !target || !BACKEND_ENABLED) return;
  if (customerScoreCache.has(customerId)) {
    target.innerHTML = renderCustomerScoreCard(customerScoreCache.get(customerId));
    return;
  }
  try {
    const response = await fetch(`/api/customers/${encodeURIComponent(customerId)}/score`, { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (handleUnauthorized(response, payload)) return;
    if (!response.ok) throw new Error(payload.error || "Não foi possível calcular o score.");
    customerScoreCache.set(customerId, payload.data);
    if (selectedCreditCustomerId === customerId && target.isConnected) {
      target.innerHTML = renderCustomerScoreCard(payload.data);
    }
  } catch (error) {
    if (target.isConnected) {
      target.innerHTML = `<section class="customer-score-card unavailable"><span>Score do cliente</span><strong>Indisponível</strong><small>${escapeHtml(error.message)}</small></section>`;
    }
  }
}

function exportCreditCustomers() {
  const rows = filteredCreditCustomersForExport().map((customer) => {
    const stats = customerCreditStats(customer.id);
    return {
      cliente: customer.name,
      cpf: customer.cpf,
      telefone: customer.whatsapp || customer.phone,
      limite: fixed(customerLimit(customer)),
      saldo_devedor: fixed(stats.open),
      parcelas_abertas: stats.openCount,
      situacao: creditStatusLabel(creditStatusFromStats(stats)),
    };
  });
  const blob = new Blob([`\uFEFF${toCsv(rows)}`], { type: "text/csv;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `crediario-${todayIso}.csv`;
  link.click();
  URL.revokeObjectURL(link.href);
}

function filteredCreditCustomersForExport() {
  const query = normalize(els.creditCustomerSearch.value);
  return db.customers.filter((customer) => {
    const stats = customerCreditStats(customer.id);
    const status = creditStatusFromStats(stats);
    const text = [customer.name, customer.whatsapp, customer.phone, customer.cpf].join(" ");
    return stats.totalCount > 0 && (!query || normalize(text).includes(query)) && (creditFilterStatus === "all" || status === creditFilterStatus);
  });
}

async function openCreditReceiveModal(customerId) {
  await loadSaleCardModalities();
  const customer = db.customers.find((item) => item.id === customerId);
  const items = db.receivables
    .filter((item) => item.customerId === customerId && item.method === "storeCredit" && item.status !== "cancelled" && receivableBalance(item) > 0)
    .sort((a, b) => a.dueDate.localeCompare(b.dueDate));
  if (!customer || !items.length) return alert("Cliente sem parcelas em aberto.");
  els.creditReceiveCustomerId.value = customerId;
  els.creditReceiveCustomerName.textContent = customer.name;
  els.creditReceiveDate.value = todayIso;
  els.creditReceiveMethod.value = "cash";
  els.creditReceiveDiscountType.value = "value";
  els.creditReceiveDiscountValue.value = "0";
  els.creditReceiveInterest.value = "0";
  els.creditReceiveFine.value = "0";
  els.creditReceiveAddition.value = "0";
  els.creditReceiveNote.value = "";
  pendingCreditReceiptKey = "";
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
  updateCreditReceiveCardField();
  els.creditReceiveModal.hidden = false;
  renderCreditReceiveTotal();
}

function closeCreditReceiveModal() {
  els.creditReceiveModal.hidden = true;
  pendingCreditReceiptKey = "";
}

function renderCreditReceiveTotal() {
  const settlement = [...els.creditReceiveList.querySelectorAll(".credit-receive-amount")].reduce((sumValue, input) => sumValue + readNumber(input.value), 0);
  const discountInput = readNumber(els.creditReceiveDiscountValue.value);
  const discount = els.creditReceiveDiscountType.value === "percent"
    ? round(settlement * discountInput / 100)
    : discountInput;
  const total = round(
    settlement
      - discount
      + readNumber(els.creditReceiveInterest.value)
      + readNumber(els.creditReceiveFine.value)
      + readNumber(els.creditReceiveAddition.value),
  );
  els.creditReceiveTotal.textContent = money.format(Math.max(0, total));
  els.creditReceiveTotal.classList.toggle("value-bad", total < 0);
}

function cardOptionsForMethod(method) {
  return saleCardModalities
    .filter((item) => item.method === method)
    .map((item) => `<option value="${escapeHtml(item.cardModalityId)}">${escapeHtml(item.name || `${paymentLabels[method]} ${item.installments || 1}x`)}</option>`)
    .join("");
}

function updateCreditReceiveCardField() {
  const method = els.creditReceiveMethod.value;
  const isCard = method === "debit" || method === "credit";
  els.creditReceiveCardModalityField.hidden = !isCard;
  els.creditReceiveCardModality.required = isCard;
  els.creditReceiveCardModality.innerHTML = isCard
    ? `<option value="">Selecione...</option>${cardOptionsForMethod(method)}`
    : "";
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
  const settlement = round(rows.reduce((sumValue, item) => sumValue + item.amount, 0));
  if (settlement <= 0) return alert("Informe pelo menos um valor para receber.");
  for (const row of rows) {
    const balance = receivableBalance(row.receivable);
    if (row.amount > balance + 0.01) return alert("Valor recebido maior que o saldo da parcela.");
  }
  const method = els.creditReceiveMethod.value;
  const discountType = els.creditReceiveDiscountType.value;
  const discountValue = round(readNumber(els.creditReceiveDiscountValue.value));
  const discount = discountType === "percent"
    ? round(settlement * discountValue / 100)
    : discountValue;
  const interest = round(readNumber(els.creditReceiveInterest.value));
  const fine = round(readNumber(els.creditReceiveFine.value));
  const addition = round(readNumber(els.creditReceiveAddition.value));
  if (discountType === "percent" && discountValue > 100) return alert("O percentual de desconto deve ser de no máximo 100%.");
  if (discount > settlement) return alert("O desconto não pode tornar o saldo recebido negativo.");
  const total = round(settlement - discount + interest + fine + addition);
  if (total < 0) return alert("O recebimento não pode resultar em valor negativo.");
  const cardModalityId = els.creditReceiveCardModality.value;
  if ((method === "debit" || method === "credit") && !cardModalityId) {
    return alert("Selecione a modalidade do cartão.");
  }
  const description = `Recebimento crediário - ${customer.name}${els.creditReceiveNote.value.trim() ? ` - ${els.creditReceiveNote.value.trim()}` : ""}`;
  if (!BACKEND_ENABLED) return showBackendRequiredMessage();
  if (!pendingCreditReceiptKey) pendingCreditReceiptKey = createId();
  try {
    const response = await fetch("/api/receivables/payments", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Idempotency-Key": pendingCreditReceiptKey,
      },
      body: JSON.stringify({
        customerId,
        method,
        cardModalityId,
        description,
        paymentDate: els.creditReceiveDate.value || todayIso,
        discountType,
        discountValue,
        interest,
        fine,
        addition,
        payments: rows.map(({ receivable, amount }) => ({ receivableId: receivable.id, amount })),
      }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      alert(payload.error || "Não foi possível registrar o recebimento.");
      return;
    }
    applyReceivablePaymentResultLocally(payload.data);
    persistLocalOnly();
    closeCreditReceiveModal();
    renderAll();
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para registrar o recebimento.");
  }
}

async function openCreditRenegotiation(receivableId) {
  await loadSaleCardModalities();
  const receivable = db.receivables.find((item) => item.id === receivableId);
  if (!receivable || receivableBalance(receivable) <= 0) return alert("Parcela sem saldo para renegociar.");
  els.creditRenegotiationReceivableId.value = receivableId;
  els.creditRenegotiationTitle.textContent = `Venda ${receivable.saleId || "-"} · Parcela ${receivable.installment || "-"}`;
  els.creditRenegotiationOpen.textContent = money.format(receivableBalance(receivable));
  els.creditRenegotiationDueDate.value = addCalendarMonthsIso(receivable.dueDate || todayIso, 1);
  els.creditRenegotiationPayment.value = "0";
  els.creditRenegotiationDiscount.value = "0";
  els.creditRenegotiationInterest.value = "0";
  els.creditRenegotiationFine.value = "0";
  els.creditRenegotiationAddition.value = "0";
  els.creditRenegotiationMethod.value = "cash";
  els.creditRenegotiationReason.value = "";
  pendingCreditRenegotiationKey = "";
  updateCreditRenegotiationCardField();
  renderCreditRenegotiationTotal();
  els.creditRenegotiationModal.hidden = false;
}

function closeCreditRenegotiation() {
  els.creditRenegotiationModal.hidden = true;
  pendingCreditRenegotiationKey = "";
}

function updateCreditRenegotiationCardField() {
  const method = els.creditRenegotiationMethod.value;
  const isCard = method === "debit" || method === "credit";
  const selectedModality = els.creditRenegotiationCardModality.value;
  els.creditRenegotiationCardField.hidden = !isCard;
  els.creditRenegotiationCardModality.required = isCard && readNumber(els.creditRenegotiationPayment.value) > 0;
  els.creditRenegotiationCardModality.innerHTML = isCard
    ? `<option value="">Selecione...</option>${cardOptionsForMethod(method)}`
    : "";
  if (
    isCard
    && [...els.creditRenegotiationCardModality.options]
      .some((option) => option.value === selectedModality)
  ) {
    els.creditRenegotiationCardModality.value = selectedModality;
  }
}

function renderCreditRenegotiationTotal() {
  const receivable = db.receivables.find((item) => item.id === els.creditRenegotiationReceivableId.value);
  if (!receivable) return;
  const newOpen = round(
    receivableBalance(receivable)
      - readNumber(els.creditRenegotiationPayment.value)
      - readNumber(els.creditRenegotiationDiscount.value)
      + readNumber(els.creditRenegotiationInterest.value)
      + readNumber(els.creditRenegotiationFine.value)
      + readNumber(els.creditRenegotiationAddition.value),
  );
  els.creditRenegotiationNewOpen.textContent = money.format(Math.max(0, newOpen));
  els.creditRenegotiationNewOpen.classList.toggle("value-bad", newOpen < 0);
  updateCreditRenegotiationCardField();
}

async function saveCreditRenegotiation(event) {
  event.preventDefault();
  const receivableId = els.creditRenegotiationReceivableId.value;
  const receivable = db.receivables.find((item) => item.id === receivableId);
  if (!receivable) return;
  const paymentAmount = round(readNumber(els.creditRenegotiationPayment.value));
  const discount = round(readNumber(els.creditRenegotiationDiscount.value));
  const interest = round(readNumber(els.creditRenegotiationInterest.value));
  const fine = round(readNumber(els.creditRenegotiationFine.value));
  const addition = round(readNumber(els.creditRenegotiationAddition.value));
  const newOpen = round(receivableBalance(receivable) - paymentAmount - discount + interest + fine + addition);
  if (newOpen < 0) return alert("A renegociação não pode gerar saldo negativo.");
  if (!els.creditRenegotiationDueDate.value) return alert("Informe o novo vencimento.");
  if (!els.creditRenegotiationReason.value.trim()) return alert("Informe o motivo da renegociação.");
  const method = els.creditRenegotiationMethod.value;
  const cardModalityId = els.creditRenegotiationCardModality.value;
  if (paymentAmount > 0 && (method === "debit" || method === "credit") && !cardModalityId) {
    return alert("Selecione a modalidade do cartão.");
  }
  if (!BACKEND_ENABLED) return showBackendRequiredMessage();
  if (!pendingCreditRenegotiationKey) pendingCreditRenegotiationKey = createId();
  try {
    const response = await fetch(`/api/receivables/${encodeURIComponent(receivableId)}/renegotiations`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Idempotency-Key": pendingCreditRenegotiationKey,
      },
      body: JSON.stringify({
        newDueDate: els.creditRenegotiationDueDate.value,
        paymentAmount,
        discount,
        interest,
        fine,
        addition,
        method,
        cardModalityId,
        reason: els.creditRenegotiationReason.value.trim(),
      }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      alert(payload.error || "Não foi possível renegociar a parcela.");
      return;
    }
    const result = payload.data || {};
    applyReceivablePaymentResultLocally({
      receivables: [result.receivable, ...(result.cardReceivables || [])],
      cash: result.cash || [],
    });
    persistLocalOnly();
    closeCreditRenegotiation();
    renderAll();
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para renegociar a parcela.");
  }
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
  const dueItems = openItems.filter((item) => item.dueDate >= todayIso);
  const paidItems = items.filter((item) => receivableBalance(item) <= 0);
  return {
    items,
    openItems,
    dueItems,
    overdueItems,
    paidItems,
    totalCount: items.length,
    openCount: openItems.length,
    dueCount: dueItems.length,
    overdueCount: overdueItems.length,
    paidCount: paidItems.length,
    open: openItems.reduce((total, item) => total + receivableBalance(item), 0),
    due: dueItems.reduce((total, item) => total + receivableBalance(item), 0),
    overdue: overdueItems.reduce((total, item) => total + receivableBalance(item), 0),
    paid: paidItems.reduce((total, item) => total + Number(item.received || item.amount || 0), 0),
  };
}

function creditStatusFromStats(stats) {
  if (stats.overdueCount > 0) return "overdue";
  if (stats.openCount <= 0) return "paid";
  return "ok";
}

function creditStatusLabel(status) {
  return status === "overdue" ? "Atrasado" : status === "paid" ? "Quitado" : "Em dia";
}

function customerLimit(customer) {
  return Number(customer.limit ?? customer.creditLimit ?? 0);
}

async function savePayable(event) {
  event.preventDefault();
  const editingId = els.payableEditingId.value;
  const supplier = db.suppliers.find((item) => item.status !== "deactivated" && normalize(item.name) === normalize(els.payableSupplier.value));
  const expenseCategory = findCatalogItem("expenseCategories", els.payableCategory.value);
  if (!supplier) return alert("Selecione um fornecedor ativo cadastrado.");
  if (!expenseCategory) return alert("Selecione uma categoria de despesa ativa.");
  const payable = {
    id: editingId || createId(),
    supplier: supplier.name,
    supplierId: supplier.id,
    category: expenseCategory.name,
    expenseCategoryId: expenseCategory.id,
    amount: readNumber(els.payableAmount.value),
    issueDate: els.payableIssue.value,
    dueDate: els.payableDue.value,
    notes: els.payableNotes.value.trim(),
    recurring: els.payableRecurring.checked,
    recurringDay: els.payableRecurring.checked
      ? Number(els.payableRecurringDay.value || String(els.payableDue.value).slice(-2))
      : null,
    paidAmount: 0,
    fee: 0,
    status: "pending",
    createdAt: new Date().toISOString(),
  };
  if (BACKEND_ENABLED) {
    try {
      const response = await fetch(
        editingId
          ? `/api/payables/${encodeURIComponent(editingId)}`
          : "/api/payables",
        {
        method: editingId ? "PUT" : "POST",
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
      resetPayableForm();
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
  resetPayableForm();
  renderAll();
}

function updatePayableRecurrenceField() {
  if (!els.payableRecurringDayField) return;
  els.payableRecurringDayField.hidden = !els.payableRecurring.checked;
  els.payableRecurringDay.required = els.payableRecurring.checked;
  if (
    els.payableRecurring.checked
    && !els.payableRecurringDay.value
    && els.payableDue.value
  ) {
    els.payableRecurringDay.value = Number(els.payableDue.value.slice(-2));
  }
}

function resetPayableForm() {
  els.payableForm.reset();
  els.payableEditingId.value = "";
  els.payableSaveButton.textContent = "Adicionar";
  els.payableFormPanel.hidden = true;
  updatePayableRecurrenceField();
}

function openNewPayableForm() {
  if (!els.payableFormPanel.hidden && !els.payableEditingId.value) {
    resetPayableForm();
    return;
  }
  els.payableForm.reset();
  els.payableEditingId.value = "";
  els.payableIssue.value = todayIso;
  els.payableDue.value = todayIso;
  els.payableSaveButton.textContent = "Adicionar";
  els.payableFormPanel.hidden = false;
  updatePayableRecurrenceField();
}

function editPayable(id) {
  const item = db.payables.find((entry) => entry.id === id);
  if (!item || ["paid", "cancelled"].includes(item.status)) return;
  if (Number(item.paidAmount || 0) > 0.009) {
    alert("Conta com pagamento parcial permite alterar apenas observações.");
  }
  els.payableEditingId.value = item.id;
  els.payableSupplier.value = item.supplier || "";
  els.payableCategory.value = item.category || "";
  els.payableAmount.value = fixed(item.amount || 0);
  els.payableIssue.value = item.issueDate || todayIso;
  els.payableDue.value = item.dueDate || todayIso;
  els.payableNotes.value = item.notes || "";
  els.payableRecurring.checked = Boolean(item.recurring);
  els.payableRecurringDay.value = item.recurringDay || "";
  els.payableSaveButton.textContent = "Salvar alterações";
  els.payableFormPanel.hidden = false;
  updatePayableRecurrenceField();
  els.payableFormPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function ensurePayableRecurrences() {
  if (!BACKEND_ENABLED || !session || payableRecurrencesChecked) return;
  payableRecurrencesChecked = true;
  try {
    const response = await fetch("/api/payables/recurrences/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}",
    });
    const payload = await response.json().catch(() => ({}));
    if (handleUnauthorized(response, payload)) return;
    if (!response.ok) throw new Error(payload.error || "Falha na recorrência.");
    if ((payload.data || []).length) {
      const payablesResponse = await fetch("/api/payables", { cache: "no-store" });
      const payablesPayload = await payablesResponse.json().catch(() => ({}));
      if (payablesResponse.ok && Array.isArray(payablesPayload.data)) {
        db.payables = payablesPayload.data;
        persistLocalOnly();
        renderPayables();
      }
    }
  } catch (error) {
    payableRecurrencesChecked = false;
    console.warn("Não foi possível atualizar contas recorrentes.", error);
  }
}

function renderPayables() {
  const query = normalize(els.payableSearch.value);
  const category = els.payableCategoryFilter.value;
  const filter = els.payableFilter.value;
  const start = els.payableStart.value || "0000-01-01";
  const end = els.payableEnd.value || "9999-12-31";
  const baseItems = db.payables.filter((item) => {
    const text = [item.supplier, item.category, item.notes].join(" ");
    if (query && !normalize(text).includes(query)) return false;
    if (category !== "all" && item.category !== category) return false;
    if (item.dueDate < start || item.dueDate > end) return false;
    return true;
  });
  const tabCounts = {
    all: baseItems.length,
    open: baseItems.filter((item) => ["pending", "today", "overdue"].includes(payableStatus(item))).length,
    overdue: baseItems.filter((item) => payableStatus(item) === "overdue").length,
    today: baseItems.filter((item) => payableStatus(item) === "today").length,
    paid: baseItems.filter((item) => payableStatus(item) === "paid").length,
  };
  if (els.payableTabAllCount) els.payableTabAllCount.textContent = tabCounts.all;
  if (els.payableTabOpenCount) els.payableTabOpenCount.textContent = tabCounts.open;
  if (els.payableTabOverdueCount) els.payableTabOverdueCount.textContent = tabCounts.overdue;
  if (els.payableTabTodayCount) els.payableTabTodayCount.textContent = tabCounts.today;
  if (els.payableTabPaidCount) els.payableTabPaidCount.textContent = tabCounts.paid;
  document.querySelectorAll("[data-payable-filter]").forEach((button) => button.classList.toggle("active", button.dataset.payableFilter === filter));
  const items = baseItems.filter((item) => {
    const status = payableStatus(item);
    if (filter === "all") return true;
    if (filter === "open") return status === "pending" || status === "today" || status === "overdue";
    if (filter === "today") return status === "today";
    return status === filter;
  }).sort((a, b) => a.dueDate.localeCompare(b.dueDate));
  const openItems = items.filter((item) => ["pending", "today", "overdue"].includes(payableStatus(item)));
  const overdueItems = items.filter((item) => payableStatus(item) === "overdue");
  const todayItems = items.filter((item) => payableStatus(item) === "today");
  const futureItems = items.filter((item) => payableStatus(item) === "pending");
  els.payableTotalOpen.textContent = money.format(openItems.reduce((total, item) => total + payableBalance(item), 0));
  els.payableTotalCount.textContent = `${openItems.length} conta${openItems.length === 1 ? "" : "s"}`;
  els.payableOverdueTotal.textContent = money.format(overdueItems.reduce((total, item) => total + payableBalance(item), 0));
  els.payableOverdueCount.textContent = `${overdueItems.length} conta${overdueItems.length === 1 ? "" : "s"}`;
  els.payableTodayTotal.textContent = money.format(todayItems.reduce((total, item) => total + payableBalance(item), 0));
  els.payableTodayCount.textContent = `${todayItems.length} conta${todayItems.length === 1 ? "" : "s"}`;
  els.payableFutureTotal.textContent = money.format(futureItems.reduce((total, item) => total + payableBalance(item), 0));
  els.payableFutureCount.textContent = `${futureItems.length} conta${futureItems.length === 1 ? "" : "s"}`;
  els.payableList.innerHTML = "";
  els.payableFooter.innerHTML = "";
  els.payableFoundCount.textContent = `${items.length} conta${items.length === 1 ? "" : "s"} encontrada${items.length === 1 ? "" : "s"}`;
  if (!items.length) {
    els.payableList.innerHTML = `<tr><td colspan="7" class="empty-cell">Nenhuma conta encontrada.</td></tr>`;
    els.payableFooter.textContent = "Mostrando 0 contas";
    renderPayableDetail(null);
    return;
  }
  if (!items.some((item) => item.id === selectedPayableId)) selectedPayableId = items[0].id;
  renderPayableDetail(db.payables.find((item) => item.id === selectedPayableId));
  items.forEach((item) => {
    const status = payableStatus(item);
    const row = document.createElement("tr");
    const initials = (item.supplier || "CP").split(" ").filter(Boolean).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
    row.className = item.id === selectedPayableId ? "selected" : "";
    row.innerHTML = `
      <td><div class="payable-supplier-cell"><span>${escapeHtml(initials)}</span><div><strong>${escapeHtml(item.supplier || "-")}</strong><small>CNPJ: -</small></div></div></td>
      <td>${escapeHtml(item.category || "-")}</td>
      <td>${escapeHtml(item.notes || item.category || "-")}</td>
      <td>${formatDate(item.dueDate)}</td>
      <td>${money.format(payableStatus(item) === "paid" ? payableTotalDue(item) : payableBalance(item))}</td>
      <td>${payableStatusBadge(item)}</td>
      <td><div class="payable-actions"></div></td>
    `;
    row.addEventListener("click", () => {
      selectedPayableId = item.id;
      renderPayables();
    });
    const actions = row.querySelector(".payable-actions");
    actions.addEventListener("click", (event) => event.stopPropagation());
    actions.append(button("Pagar", "primary payable-pay-button", () => openPayablePaymentModal(item.id), !["pending", "today", "overdue"].includes(status)));
    els.payableList.append(row);
  });
  els.payableFooter.innerHTML = `
    <span>Mostrando 1 a ${items.length} de ${items.length} conta${items.length === 1 ? "" : "s"}</span>
    <div class="payable-pagination"><button type="button" disabled>Anterior</button><button type="button" class="active">1</button><button type="button" disabled>Próximo</button></div>
  `;
}

function renderPayableDetail(item) {
  if (!els.payableDetailPanel) return;
  if (!item) {
    els.payableDetailPanel.className = "panel payable-detail-panel empty";
    els.payableDetailPanel.textContent = "Selecione uma conta para visualizar o resumo.";
    return;
  }
  const status = payableStatus(item);
  const finalAmount = payableTotalDue(item);
  const openAmount = payableBalance(item);
  els.payableDetailPanel.className = "panel payable-detail-panel";
  els.payableDetailPanel.innerHTML = `
    <div class="payable-detail-head">
      <span>${escapeHtml((item.supplier || "CP").split(" ").filter(Boolean).slice(0, 2).map((part) => part[0]).join("").toUpperCase() || "CP")}</span>
      <div><strong>${escapeHtml(item.supplier || "-")}</strong><small>${escapeHtml(item.category || "-")}</small><em>${escapeHtml(item.notes || "Sem observação")}</em></div>
      ${payableStatusBadge(item)}
    </div>
    <div class="payable-detail-list">
      <div><span>Valor original</span><strong>${money.format(item.amount || 0)}</strong></div>
      <div><span>Juros</span><strong>${money.format((Number(item.interest || 0) || Number(item.fine || 0)) ? item.interest || 0 : item.fee || 0)}</strong></div>
      <div><span>Multa</span><strong>${money.format(item.fine || 0)}</strong></div>
      <div><span>Desconto</span><strong>${money.format(item.discount || 0)}</strong></div>
      <div><span>Total</span><strong class="${status === "paid" ? "value-ok" : status === "overdue" ? "value-bad" : ""}">${money.format(finalAmount)}</strong></div>
      <div><span>Já pago</span><strong>${money.format(item.paidAmount || 0)}</strong></div>
      <div><span>Saldo em aberto</span><strong class="${openAmount > 0 ? "value-bad" : "value-ok"}">${money.format(openAmount)}</strong></div>
      <div><span>Emissão</span><strong>${formatDate(item.issueDate)}</strong></div>
      <div><span>Vencimento</span><strong>${formatDate(item.dueDate)}</strong></div>
      <div><span>Pagamento</span><strong>${item.paidAt ? formatDate(item.paidAt) : "-"}</strong></div>
      <div><span>Recorrência</span><strong>${item.recurring ? `Mensal, dia ${item.recurringDay}` : "Não"}</strong></div>
    </div>
    ${renderPayableHistory(item)}
    <div class="payable-detail-actions">
      <button class="primary payable-pay-button" type="button" id="payableDetailPayButton"${!["pending", "today", "overdue"].includes(status) ? " disabled" : ""}>Pagar</button>
      <button class="ghost" type="button" id="payableDetailEditButton"${["paid", "cancelled"].includes(status) ? " disabled" : ""}>Editar</button>
      <button class="ghost" type="button" id="payableDetailCancelButton"${["paid", "cancelled"].includes(status) || Number(item.paidAmount || 0) > 0.009 ? " disabled" : ""}>Cancelar</button>
    </div>
  `;
  els.payableDetailPanel.querySelector("#payableDetailPayButton").addEventListener("click", () => openPayablePaymentModal(item.id));
  els.payableDetailPanel.querySelector("#payableDetailEditButton").addEventListener("click", () => editPayable(item.id));
  els.payableDetailPanel.querySelector("#payableDetailCancelButton").addEventListener("click", () => cancelPayable(item.id));
  els.payableDetailPanel.querySelectorAll("[data-reverse-payable-payment]").forEach((control) => {
    control.addEventListener("click", () => reversePayablePayment(item.id, control.dataset.reversePayablePayment));
  });
}

function renderPayableHistory(item) {
  const payments = item.payments || [];
  const events = item.events || [];
  if (!payments.length && !events.length) {
    return '<div class="payable-history empty">Nenhum evento financeiro registrado.</div>';
  }
  const paymentRows = payments.map((payment) => `
    <article class="${payment.status === "reversed" ? "reversed" : ""}">
      <div>
        <strong>Pagamento ${money.format(payment.amount || 0)}</strong>
        <small>${formatDateTime(payment.createdAt)} | ${escapeHtml(paymentLabels[payment.method] || payment.method || "-")}</small>
        <small>Juros ${money.format(payment.interestAmount || 0)} | Multa ${money.format(payment.fineAmount || 0)} | Desconto ${money.format(payment.discountAmount || 0)}</small>
      </div>
      ${payment.status === "active"
        ? `<button type="button" class="ghost" data-reverse-payable-payment="${escapeHtml(payment.id)}">Estornar</button>`
        : "<span>Estornado</span>"}
    </article>
  `).join("");
  const eventRows = events
    .filter((event) => !["payment", "payment_reversal"].includes(event.eventType))
    .map((event) => `
      <article>
        <div>
          <strong>${escapeHtml({
            created: "Conta cadastrada",
            updated: "Conta alterada",
            cancelled: "Conta cancelada",
            recurrence: "Ocorrência recorrente",
          }[event.eventType] || event.eventType)}</strong>
          <small>${formatDateTime(event.createdAt)} | ${escapeHtml(event.userName || "Sistema")}</small>
        </div>
      </article>
    `).join("");
  return `<div class="payable-history"><h3>Histórico</h3>${paymentRows}${eventRows}</div>`;
}

function openPayablePaymentModal(id) {
  const item = db.payables.find((entry) => entry.id === id);
  if (!item || ["paid", "cancelled"].includes(payableStatus(item))) return;
  const openAmount = payableBalance(item);
  els.payablePaymentId.value = id;
  els.payablePaymentTitle.textContent = `${item.supplier || "Fornecedor"} | ${item.notes || item.category || "Conta a pagar"}`;
  els.payablePaymentOriginal.textContent = money.format(item.amount || 0);
  els.payablePaymentOpen.textContent = money.format(openAmount);
  els.payablePaymentMethod.value = "pix";
  els.payablePaymentInterest.value = "0.00";
  els.payablePaymentFine.value = "0.00";
  els.payablePaymentDiscount.value = "0.00";
  els.payablePaymentAmount.value = fixed(openAmount);
  els.payablePaymentNote.value = "";
  els.payablePaymentHistory.innerHTML = renderPayableHistory(item);
  els.payablePaymentHistory.querySelectorAll("[data-reverse-payable-payment]").forEach((control) => {
    control.addEventListener("click", () => {
      closePayablePaymentModal();
      reversePayablePayment(item.id, control.dataset.reversePayablePayment);
    });
  });
  renderPayablePaymentTotal();
  els.payablePaymentModal.hidden = false;
}

function closePayablePaymentModal() {
  els.payablePaymentModal.hidden = true;
  els.payablePaymentForm.reset();
  els.payablePaymentId.value = "";
}

function renderPayablePaymentTotal() {
  const item = db.payables.find((entry) => entry.id === els.payablePaymentId.value);
  const currentOpen = payableBalance(item || {});
  const interest = readNumber(els.payablePaymentInterest.value);
  const fine = readNumber(els.payablePaymentFine.value);
  const discount = readNumber(els.payablePaymentDiscount.value);
  const openAmount = Math.max(0, round(currentOpen + interest + fine - discount));
  const paidNow = readNumber(els.payablePaymentAmount.value);
  const remaining = Math.max(0, round(openAmount - paidNow));
  els.payablePaymentOpen.textContent = money.format(openAmount);
  els.payablePaymentRemaining.textContent = money.format(remaining);
}

function payableStatusBadge(item) {
  const status = payableStatus(item);
  const labels = { paid: "Pago", cancelled: "Cancelada", overdue: "Vencida", today: "Vence hoje", pending: "A vencer" };
  const isPartial = !["paid", "cancelled"].includes(status) && Number(item.paidAmount || 0) > 0;
  const extra = isPartial ? `<small>${money.format(payableBalance(item))}</small>` : status === "overdue" ? `<small>${diffDays(item.dueDate, todayIso)} dias de atraso</small>` : status === "pending" ? `<small>${diffDays(todayIso, item.dueDate)} dias</small>` : "";
  return `<span class="payable-status ${isPartial ? "partial" : status}">${isPartial ? "Parcial" : labels[status]}${extra}</span>`;
}

async function savePayablePayment(event) {
  event.preventDefault();
  const id = els.payablePaymentId.value;
  const item = db.payables.find((entry) => entry.id === id);
  if (!item) return;
  const interest = readNumber(els.payablePaymentInterest.value);
  const fine = readNumber(els.payablePaymentFine.value);
  const discount = readNumber(els.payablePaymentDiscount.value);
  const openAmount = Math.max(0, round(payableBalance(item) + interest + fine - discount));
  const amount = readNumber(els.payablePaymentAmount.value);
  if (amount < 0 || (amount <= 0 && openAmount > 0.01)) {
    return alert("Informe o valor pago ou um desconto que quite a conta.");
  }
  if (amount - openAmount > 0.01) return alert("O valor pago não pode ser maior que o saldo em aberto.");
  const method = els.payablePaymentMethod.value;
  const note = els.payablePaymentNote.value.trim();
  if (BACKEND_ENABLED) {
    try {
      const supplierCredit = method === "supplierCredit";
      const response = await fetch(
        supplierCredit
          ? `/api/payables/${encodeURIComponent(id)}/supplier-credit`
          : `/api/payables/${encodeURIComponent(id)}/pay`,
        {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": createId(),
        },
        body: JSON.stringify(supplierCredit
          ? { amount }
          : { interest, fine, discount, amount, method, note }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        alert(payload.error || "Não foi possível baixar a conta.");
        return;
      }
      if (supplierCredit) {
        applyPayableLocally(payload.data?.payable);
        db.supplierCredits = payload.data?.credits || db.supplierCredits;
      } else {
        applyPayablePaymentResultLocally(payload.data);
      }
      persistLocalOnly();
      closePayablePaymentModal();
      renderAll();
      return;
    } catch (error) {
      console.warn(error);
      alert("Não foi possível conectar ao servidor para baixar a conta.");
      return;
    }
  }
  item.interest = round(Number(item.interest || 0) + interest);
  item.fine = round(Number(item.fine || 0) + fine);
  item.fee = round(item.interest + item.fine);
  item.discount = round(Number(item.discount || 0) + discount);
  item.paidAmount = round(Number(item.paidAmount || 0) + amount);
  item.openAmount = round(openAmount - amount);
  item.status = item.openAmount <= 0.01 ? "paid" : "pending";
  item.paidAt = new Date().toISOString();
  const description = note ? `${item.category} - ${note}` : item.category;
  addCash("out", "contas a pagar", description, method, amount, item.id, item.paidAt);
  persist();
  closePayablePaymentModal();
  renderAll();
}

async function reversePayablePayment(payableId, paymentId) {
  const reason = prompt("Informe o motivo do estorno do pagamento:");
  if (!reason?.trim()) return;
  try {
    const response = await fetch(
      `/api/payables/${encodeURIComponent(payableId)}/payments/${encodeURIComponent(paymentId)}/reverse`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": createId(),
        },
        body: JSON.stringify({ reason: reason.trim() }),
      },
    );
    const payload = await response.json().catch(() => ({}));
    if (handleUnauthorized(response, payload)) return;
    if (!response.ok) {
      alert(payload.error || "Não foi possível estornar o pagamento.");
      return;
    }
    applyPayablePaymentResultLocally(payload.data);
    persistLocalOnly();
    renderAll();
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para estornar o pagamento.");
  }
}

async function cancelPayable(payableId) {
  const reason = prompt("Informe o motivo do cancelamento da conta:");
  if (!reason?.trim()) return;
  try {
    const response = await fetch(
      `/api/payables/${encodeURIComponent(payableId)}/cancel`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason: reason.trim() }),
      },
    );
    const payload = await response.json().catch(() => ({}));
    if (handleUnauthorized(response, payload)) return;
    if (!response.ok) {
      alert(payload.error || "Não foi possível cancelar a conta.");
      return;
    }
    applyPayableLocally(payload.data);
    persistLocalOnly();
    renderAll();
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para cancelar a conta.");
  }
}

async function saveCashMovement(event) {
  event.preventDefault();
  const direction = els.cashMovementType.value;
  const expenseType = direction === "out" ? els.cashExpenseType.value.trim() : "";
  const expenseCategory = direction === "out"
    ? findCatalogItem("expenseCategories", expenseType)
    : null;
  if (direction === "out" && !expenseType) return alert("Selecione o tipo de despesa.");
  if (direction === "out" && !expenseCategory) return alert("Selecione uma categoria de despesa ativa.");
  const movement = {
    id: createId(),
    direction,
    type: direction === "out" ? expenseCategory.name : "manual",
    expenseCategoryId: expenseCategory?.id || "",
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
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": movement.id || createId(),
        },
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
      updateCashExpenseField();
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
  updateCashExpenseField();
  els.cashMovementPanel.hidden = true;
  renderAll();
}

async function reverseCashMovement(movementId) {
  const reason = prompt("Informe o motivo do estorno da movimentação:");
  if (!reason?.trim()) return;
  try {
    const response = await fetch(
      `/api/cash-movements/${encodeURIComponent(movementId)}/reverse`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": createId(),
        },
        body: JSON.stringify({ reason: reason.trim() }),
      },
    );
    const payload = await response.json().catch(() => ({}));
    if (handleUnauthorized(response, payload)) return;
    if (!response.ok) {
      alert(payload.error || "Não foi possível estornar a movimentação.");
      return;
    }
    const reversedAt = payload.data?.movement?.createdAt || new Date().toISOString();
    db.cash = db.cash.map((item) => (
      item.id === payload.data?.reversedMovementId
        ? { ...item, reversedAt }
        : item
    ));
    if (payload.data?.movement) {
      db.cash = [
        payload.data.movement,
        ...db.cash.filter((item) => item.id !== payload.data.movement.id),
      ];
    }
    persistLocalOnly();
    renderAll();
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para estornar a movimentação.");
  }
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
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": createId(),
        },
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
  const todayItems = db.cash.filter((item) => storeOperationalDateKey(item.createdAt) === todayIso);
  els.cashTotal.textContent = money.format(total);
  els.cashInToday.textContent = money.format(todayItems.filter((item) => item.direction === "in").reduce((value, item) => value + item.amount, 0));
  els.cashOutToday.textContent = money.format(todayItems.filter((item) => item.direction === "out").reduce((value, item) => value + item.amount, 0));
  const start = els.cashStart.value || "0000-01-01";
  const end = els.cashEnd.value || "9999-12-31";
  const method = els.cashMethodFilter.value;
  const movementType = els.cashTypeFilter.value;
  const expenseType = els.cashExpenseFilter?.value || "all";
  let balance = 0;
  const rows = db.cash.slice().sort((a, b) => a.createdAt.localeCompare(b.createdAt)).map((item) => {
    balance += item.direction === "in" ? item.amount : -item.amount;
    return {
      ...item,
      balance: item.resultingBalance ?? balance,
      operationalDate: storeOperationalDateKey(item.createdAt),
    };
  }).filter((item) => item.operationalDate >= start
    && item.operationalDate <= end
    && (method === "all" || item.method === method)
    && (movementType === "all" || item.direction === movementType)
    && (expenseType === "all" || (item.direction === "out" && item.type === expenseType)));
  renderCashExpenseSummary(rows);
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
        <p>${escapeHtml(cashMovementMeta(item))}</p>
      </div>
      <div class="cash-row-value">
        <strong>${isIn ? "+" : "-"} ${money.format(item.amount)}</strong>
        <span>Saldo: ${money.format(item.balance)}</span>
      </div>
      <button type="button" class="ghost cash-reversal-button"${item.reversalOfId || item.reversedAt ? " disabled" : ""}>Estornar</button>
    `;
    row.querySelector(".cash-reversal-button").addEventListener("click", () => reverseCashMovement(item.id));
    els.cashTimeline.append(row);
  });
  els.cashFooter.innerHTML = `
    <span>Mostrando ${rows.length} de ${rows.length} movimentaç${rows.length === 1 ? "ão" : "ões"}</span>
    <div class="cash-pagination"><button type="button" disabled>Anterior</button><button type="button" class="active">1</button><button type="button" disabled>Próximo</button></div>
  `;
}

function cashMovementMeta(item) {
  const payment = paymentLabels[item.method] || item.method || "-";
  const details = [];
  if (item.direction === "out" && item.type && item.type !== "manual") details.push(item.type);
  details.push(payment);
  if (item.originType) details.push(`Origem: ${item.originType}`);
  if (item.userName) details.push(`Operador: ${item.userName}`);
  if (item.reversalOfId) details.push("Movimentação de estorno");
  if (item.reversedAt) details.push("Estornada");
  return details.join(" | ");
}

function filteredCashMovements() {
  const start = els.cashStart.value || "0000-01-01";
  const end = els.cashEnd.value || "9999-12-31";
  const method = els.cashMethodFilter.value;
  const movementType = els.cashTypeFilter.value;
  const expenseType = els.cashExpenseFilter?.value || "all";
  return db.cash
    .slice()
    .sort((a, b) => String(a.createdAt || "").localeCompare(String(b.createdAt || "")))
    .filter((item) => {
      const operationalDate = storeOperationalDateKey(item.createdAt);
      return operationalDate >= start
        && operationalDate <= end
        && (method === "all" || item.method === method)
        && (movementType === "all" || item.direction === movementType)
        && (expenseType === "all" || (item.direction === "out" && item.type === expenseType));
    });
}

function exportCashMovements() {
  const rows = filteredCashMovements().map((item) => ({
    data_hora: formatDateTime(item.createdAt),
    tipo: item.direction === "in" ? "Entrada" : "Saída",
    descricao: item.description || item.type || "",
    origem: item.originType || "",
    referencia: item.originId || item.refId || "",
    operador: item.userName || "",
    forma_pagamento: paymentLabels[item.method] || item.method || "",
    tipo_despesa: item.direction === "out" ? item.type || "" : "",
    valor: fixed(item.amount || 0),
    saldo_resultante: fixed(item.resultingBalance ?? 0),
    estorno_de: item.reversalOfId || "",
  }));
  const blob = new Blob([`\uFEFF${toCsv(rows)}`], { type: "text/csv;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `caixa-${els.cashStart.value || todayIso}-${els.cashEnd.value || todayIso}.csv`;
  link.click();
  URL.revokeObjectURL(link.href);
}

function renderCashExpenseSummary(rows) {
  if (!els.cashExpenseSummary || !els.cashExpenseTotal) return;
  const expenses = rows.filter((item) => item.direction === "out");
  const grouped = expenses.reduce((acc, item) => {
    const key = item.type && item.type !== "manual" ? item.type : "Outros";
    acc[key] = round((acc[key] || 0) + Number(item.amount || 0));
    return acc;
  }, {});
  const entries = Object.entries(grouped).sort((a, b) => b[1] - a[1]);
  const total = round(entries.reduce((sum, [, value]) => sum + value, 0));
  els.cashExpenseTotal.textContent = money.format(total);
  els.cashExpenseSummary.classList.toggle("empty", entries.length === 0);
  els.cashExpenseSummary.innerHTML = entries.length
    ? entries.map(([type, value]) => `
      <article>
        <span>${escapeHtml(type)}</span>
        <strong>${money.format(value)}</strong>
      </article>
    `).join("")
    : "Nenhuma despesa no período.";
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

function scheduleCardReceivablesLoad() {
  window.clearTimeout(cardReceivableLoadTimer);
  cardReceivableLoadTimer = window.setTimeout(() => loadCardReceivables(true), 220);
}

async function loadCardReceivables(resetPage = false) {
  if (!BACKEND_ENABLED || cardReceivableLoading) return;
  if (resetPage) cardReceivablePage = 1;
  const params = new URLSearchParams({ page: String(cardReceivablePage), pageSize: "20" });
  [
    ["search", els.cardReceivableSearch.value.trim()],
    ["method", els.cardReceivableMethod.value],
    ["status", els.cardReceivableStatus.value],
    ["start", els.cardReceivableStart.value],
    ["end", els.cardReceivableEnd.value],
  ].forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  cardReceivableLoading = true;
  renderCards();
  try {
    const response = await fetch(`/api/card-reconciliations/receivables?${params}`, { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (handleUnauthorized(response, payload)) return;
    if (!response.ok) throw new Error(payload.error || "Não foi possível carregar os recebíveis.");
    cardReceivableData = payload.data;
  } catch (error) {
    cardReceivableData = { error: error.message || "Não foi possível carregar os recebíveis." };
  } finally {
    cardReceivableLoading = false;
    renderCards();
  }
}

function cardReceivableStatusLabel(status) {
  return {
    cardPending: "Pendente",
    cardPartial: "Parcialmente recebido",
    paid: "Recebido",
    cardDivergent: "Com divergência",
    cancelled: "Cancelado",
  }[status] || status || "-";
}

function renderCards() {
  if (!els.cardReceivableList) return;
  const summary = cardReceivableData?.summary || {};
  els.cardOpenTotal.textContent = money.format(summary.openTotal || 0);
  els.cardDueToday.textContent = money.format(summary.dueToday || 0);
  els.cardReceivedMonth.textContent = money.format(summary.receivedMonth || 0);
  els.cardDivergenceTotal.textContent = money.format(summary.divergenceTotal || 0);
  els.cardReconcileSelectedButton.disabled = selectedCardReceivables.size === 0;
  if (cardReceivableLoading) {
    els.cardReceivableState.hidden = false;
    els.cardReceivableState.className = "card-reconciliation-state loading";
    els.cardReceivableState.textContent = "Carregando recebíveis...";
    els.cardReceivableList.innerHTML = "";
    return;
  }
  if (cardReceivableData?.error) {
    els.cardReceivableState.hidden = false;
    els.cardReceivableState.className = "card-reconciliation-state error";
    els.cardReceivableState.innerHTML = `${escapeHtml(cardReceivableData.error)} <button class="ghost" type="button">Tentar novamente</button>`;
    els.cardReceivableState.querySelector("button").addEventListener("click", () => loadCardReceivables());
    els.cardReceivableList.innerHTML = "";
    return;
  }
  const items = cardReceivableData?.items || [];
  els.cardReceivableState.hidden = items.length > 0;
  if (!items.length) {
    els.cardReceivableState.className = "card-reconciliation-state empty";
    els.cardReceivableState.textContent = "Nenhum recebível encontrado para os filtros informados.";
    els.cardReceivableList.innerHTML = "";
    renderCardReceivablePagination();
    return;
  }
  els.cardReceivableList.innerHTML = `
    <div class="card-receivable-row card-receivable-head">
      <span></span><span>Venda</span><span>Modalidade</span><span>Bruto</span>
      <span>Taxa</span><span>Líquido esperado</span><span>Recebido</span>
      <span>Diferença</span><span>Previsão</span><span>Situação</span><span>Ações</span>
    </div>
    ${items.map((item) => {
      const eligible = ["cardPending", "cardPartial"].includes(item.status);
      return `
        <article class="card-receivable-row">
          <label class="card-select"><input type="checkbox" data-card-select="${escapeHtml(item.id)}" ${selectedCardReceivables.has(item.id) ? "checked" : ""} ${eligible ? "" : "disabled"}><span></span></label>
          <div><strong>${escapeHtml(item.saleId || "-")}</strong><small>${escapeHtml(item.customerName || "Venda simples")}</small></div>
          <span>${escapeHtml(item.modalityName || paymentLabels[item.method] || item.method)}</span>
          <span>${money.format(item.grossAmount || 0)}</span>
          <span>${fixed(item.taxPercent || 0)}%</span>
          <strong>${money.format(item.amount || 0)}</strong>
          <span>${money.format(item.received || 0)}</span>
          <span class="${Math.abs(Number(item.differenceAmount || 0)) > 0.01 ? "value-bad" : ""}">${money.format(item.differenceAmount || 0)}</span>
          <span>${formatDate(item.dueDate)}</span>
          <span class="status-pill ${escapeHtml(item.status)}">${escapeHtml(cardReceivableStatusLabel(item.status))}</span>
          <div class="card-row-actions">
            <button class="ghost" type="button" data-card-detail="${escapeHtml(item.id)}">Detalhes</button>
            ${eligible ? `<button class="primary" type="button" data-card-reconcile="${escapeHtml(item.id)}">Conciliar</button>` : ""}
          </div>
        </article>
      `;
    }).join("")}
  `;
  els.cardReceivableList.querySelectorAll("[data-card-select]").forEach((input) => {
    input.addEventListener("input", () => {
      const item = items.find((candidate) => candidate.id === input.dataset.cardSelect);
      if (!item) return;
      if (input.checked) selectedCardReceivables.set(item.id, item);
      else selectedCardReceivables.delete(item.id);
      els.cardReconcileSelectedButton.disabled = selectedCardReceivables.size === 0;
    });
  });
  els.cardReceivableList.querySelectorAll("[data-card-reconcile]").forEach((control) => {
    control.addEventListener("click", () => {
      const item = items.find((candidate) => candidate.id === control.dataset.cardReconcile);
      if (item) openCardReconciliation([item]);
    });
  });
  els.cardReceivableList.querySelectorAll("[data-card-detail]").forEach((control) => {
    control.addEventListener("click", () => {
      const item = items.find((candidate) => candidate.id === control.dataset.cardDetail);
      if (item) openCardReceivableDetail(item);
    });
  });
  renderCardReceivablePagination();
}

function renderCardReceivablePagination() {
  const pagination = cardReceivableData?.pagination;
  if (!pagination) {
    els.cardReceivablePagination.innerHTML = "";
    return;
  }
  els.cardReceivablePagination.innerHTML = `
    <button class="ghost" type="button" data-card-page="${pagination.page - 1}" ${pagination.page <= 1 ? "disabled" : ""}>Anterior</button>
    <span>Página ${pagination.page} de ${pagination.pages} · ${pagination.total} recebíveis</span>
    <button class="ghost" type="button" data-card-page="${pagination.page + 1}" ${pagination.page >= pagination.pages ? "disabled" : ""}>Próxima</button>
  `;
  els.cardReceivablePagination.querySelectorAll("[data-card-page]").forEach((button) => {
    button.addEventListener("click", () => {
      cardReceivablePage = Number(button.dataset.cardPage || 1);
      loadCardReceivables();
    });
  });
}

function openCardReconciliation(explicitItems = null) {
  const items = explicitItems || [...selectedCardReceivables.values()];
  if (!items.length) return;
  pendingCardReconciliationKey = createId();
  els.cardReconciliationDate.value = todayIso;
  els.cardReconciliationNote.value = "";
  els.cardReconciliationSubtitle.textContent = `${items.length} recebível${items.length === 1 ? "" : "is"} selecionado${items.length === 1 ? "" : "s"}`;
  els.cardReconciliationItems.innerHTML = items.map((item) => `
    <article class="card-reconciliation-item" data-card-reconciliation-item="${escapeHtml(item.id)}" data-version="${Number(item.version || 0)}" data-balance="${Number(item.openAmount || 0)}">
      <div><strong>${escapeHtml(item.saleId || "-")} · ${escapeHtml(item.modalityName || paymentLabels[item.method] || item.method)}</strong><small>Saldo esperado ${money.format(item.openAmount || 0)} · previsão ${formatDate(item.dueDate)}</small></div>
      <label class="field">Valor atribuído<input class="card-allocation" type="number" min="0.01" step="0.01" value="${fixed(item.openAmount || 0)}" required></label>
      <label class="card-divergence-toggle"><input class="card-close-divergence" type="checkbox"> Encerrar com divergência</label>
      <label class="field card-divergence-note">Justificativa<input class="card-divergence-reason" type="text" maxlength="240" disabled></label>
    </article>
  `).join("");
  els.cardReconciliationItems.querySelectorAll(".card-close-divergence").forEach((checkbox) => {
    checkbox.addEventListener("input", () => {
      const reason = checkbox.closest(".card-reconciliation-item").querySelector(".card-divergence-reason");
      reason.disabled = !checkbox.checked;
      if (!checkbox.checked) reason.value = "";
    });
  });
  els.cardReconciliationTotal.value = fixed(items.reduce((total, item) => total + Number(item.openAmount || 0), 0));
  els.cardReconciliationModal.hidden = false;
  updateCardReconciliationTotals();
}

function closeCardReconciliation() {
  if (els.cardReconciliationSubmitButton.disabled) return;
  els.cardReconciliationModal.hidden = true;
  pendingCardReconciliationKey = "";
}

function updateCardReconciliationTotals() {
  const total = [...els.cardReconciliationItems.querySelectorAll(".card-allocation")]
    .reduce((value, input) => value + readNumber(input.value), 0);
  els.cardReconciliationAllocatedTotal.textContent = money.format(total);
  els.cardReconciliationAllocatedTotal.classList.toggle("value-bad", Math.abs(total - readNumber(els.cardReconciliationTotal.value)) > 0.01);
}

async function submitCardReconciliation(event) {
  event.preventDefault();
  const items = [...els.cardReconciliationItems.querySelectorAll("[data-card-reconciliation-item]")].map((row) => ({
    receivableId: row.dataset.cardReconciliationItem,
    expectedVersion: Number(row.dataset.version),
    expectedBalance: readNumber(row.dataset.balance),
    amount: readNumber(row.querySelector(".card-allocation").value),
    closeWithDivergence: row.querySelector(".card-close-divergence").checked,
    divergenceNote: row.querySelector(".card-divergence-reason").value.trim(),
  }));
  els.cardReconciliationSubmitButton.disabled = true;
  try {
    const response = await fetch("/api/card-reconciliations", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Idempotency-Key": pendingCardReconciliationKey },
      body: JSON.stringify({
        receiptDate: els.cardReconciliationDate.value,
        totalReceived: readNumber(els.cardReconciliationTotal.value),
        note: els.cardReconciliationNote.value.trim(),
        items,
      }),
    });
    const result = await response.json().catch(() => ({}));
    if (handleUnauthorized(response, result)) return;
    if (!response.ok) throw new Error(result.error || "Não foi possível concluir a conciliação.");
    (result.data?.receivables || []).forEach((updated) => {
      db.receivables = db.receivables.map((item) => item.id === updated.id ? updated : item);
    });
    if (result.data?.cash) db.cash = [result.data.cash, ...db.cash.filter((item) => item.id !== result.data.cash.id)];
    persistLocalOnly();
    selectedCardReceivables.clear();
    els.cardReconciliationModal.hidden = true;
    pendingCardReconciliationKey = "";
    await loadCardReceivables(true);
  } catch (error) {
    alert(error.message || "Não foi possível concluir a conciliação.");
  } finally {
    els.cardReconciliationSubmitButton.disabled = false;
  }
}

function openCardReceivableDetail(item) {
  els.cardReceivableDetailTitle.textContent = `Recebível ${item.saleId || "-"}`;
  els.cardReceivableDetailSubtitle.textContent = `${item.modalityName || paymentLabels[item.method] || item.method} · ${cardReceivableStatusLabel(item.status)}`;
  const history = item.reconciliations || [];
  els.cardReceivableDetailBody.innerHTML = `
    <div class="card-detail-summary">
      <span>Bruto<strong>${money.format(item.grossAmount || 0)}</strong></span>
      <span>Taxa<strong>${fixed(item.taxPercent || 0)}%</strong></span>
      <span>Líquido esperado<strong>${money.format(item.amount || 0)}</strong></span>
      <span>Recebido<strong>${money.format(item.received || 0)}</strong></span>
      <span>Saldo<strong>${money.format(item.openAmount || 0)}</strong></span>
      <span>Diferença<strong>${money.format(item.differenceAmount || 0)}</strong></span>
    </div>
    <div class="card-reconciliation-history">
      ${history.length ? history.map((entry) => `
        <article class="${entry.status === "reversed" ? "reversed" : ""}">
          <div><strong>${formatDate(entry.receiptDate)} · ${money.format(entry.allocatedAmount || 0)}</strong><small>${escapeHtml(entry.userName || "Operador")} · ${entry.itemCount > 1 ? `Lote com ${entry.itemCount} itens` : "Individual"}</small></div>
          <span class="status-pill ${escapeHtml(entry.status)}">${entry.status === "reversed" ? "Estornado" : "Recebido"}</span>
          ${entry.status === "active" ? `<button class="ghost" type="button" data-card-reversal="${escapeHtml(entry.reconciliationId)}">Estornar</button>` : `<small>${escapeHtml(entry.reversalReason || "")}</small>`}
        </article>
      `).join("") : '<p class="empty">Nenhuma conciliação registrada.</p>'}
    </div>
  `;
  els.cardReceivableDetailBody.querySelectorAll("[data-card-reversal]").forEach((button) => {
    button.addEventListener("click", () => reverseCardReconciliationFromDetail(button.dataset.cardReversal));
  });
  els.cardReceivableDetailModal.hidden = false;
}

function closeCardReceivableDetail() {
  els.cardReceivableDetailModal.hidden = true;
}

async function reverseCardReconciliationFromDetail(reconciliationId) {
  const reason = prompt("Informe o motivo do estorno da conciliação:");
  if (!reason?.trim()) return;
  try {
    const response = await fetch(`/api/card-reconciliations/${encodeURIComponent(reconciliationId)}/reversal`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Idempotency-Key": createId() },
      body: JSON.stringify({ reason: reason.trim() }),
    });
    const payload = await response.json().catch(() => ({}));
    if (handleUnauthorized(response, payload)) return;
    if (!response.ok) throw new Error(payload.error || "Não foi possível estornar a conciliação.");
    (payload.data?.receivables || []).forEach((updated) => {
      db.receivables = db.receivables.map((item) => item.id === updated.id ? updated : item);
    });
    if (payload.data?.cash) db.cash = [payload.data.cash, ...db.cash.filter((item) => item.id !== payload.data.cash.id)];
    persistLocalOnly();
    closeCardReceivableDetail();
    await loadCardReceivables();
  } catch (error) {
    alert(error.message || "Não foi possível estornar a conciliação.");
  }
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
  els.dashPayablesOpen.textContent = money.format(openPayables.reduce((total, item) => total + payableBalance(item), 0));
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
  const openPayables = db.payables.filter((item) => payableStatus(item) !== "paid").reduce((total, item) => total + payableBalance(item), 0);
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

function dashboardQuery() {
  const preset = els.dashSalesRange.value || "30days";
  const params = new URLSearchParams({ period: preset });
  if (preset === "custom") {
    if (!els.dashCustomStart.value || !els.dashCustomEnd.value) {
      throw new Error("Informe as datas inicial e final do período.");
    }
    if (els.dashCustomStart.value > els.dashCustomEnd.value) {
      throw new Error("A data inicial não pode ser posterior à data final.");
    }
    params.set("start", els.dashCustomStart.value);
    params.set("end", els.dashCustomEnd.value);
  }
  return params;
}

function updateDashboardPeriodControls() {
  const custom = els.dashSalesRange.value === "custom";
  els.dashCustomStartField.hidden = !custom;
  els.dashCustomEndField.hidden = !custom;
  const operationalDate = dashboardKnownToday || storeOperationalDateKey(new Date());
  if (custom && !els.dashCustomStart.value) els.dashCustomStart.value = operationalDate;
  if (custom && !els.dashCustomEnd.value) els.dashCustomEnd.value = operationalDate;
}

function startDashboardDayWatch() {
  if (dashboardDayWatchTimer) return;
  dashboardDayWatchTimer = window.setInterval(checkDashboardOperationalDay, 60000);
}

function checkDashboardOperationalDay() {
  const currentDate = storeOperationalDateKey(new Date());
  if (!currentDate || currentDate === dashboardKnownToday) return false;
  dashboardKnownToday = currentDate;
  alertsLoaded = false;
  customerScoreCache.clear();
  invalidateDashboardCache();
  if (session) {
    renderDashboard();
    loadAlerts(true);
  }
  return true;
}

function renderDashboard() {
  if (!BACKEND_ENABLED || !session) return;
  updateDashboardPeriodControls();
  let key;
  try {
    key = dashboardQuery().toString();
  } catch (error) {
    setDashboardState("error", error.message);
    return;
  }
  if (dashboardApiCache && dashboardApiKey === key) {
    renderDashboardFromSummary(dashboardApiCache);
    return;
  }
  requestDashboardSummary();
}

function setDashboardState(state, message = "") {
  els.dashboardStatus.hidden = state === "success";
  els.dashboardStatus.className = `dashboard-status ${state}`;
  if (state === "loading") {
    els.dashboardStatus.textContent = "Carregando indicadores...";
  } else if (state === "error") {
    els.dashboardStatus.innerHTML = `${escapeHtml(message || "Não foi possível carregar o Dashboard.")}<button class="ghost" type="button" data-dashboard-retry>Tentar novamente</button>`;
    els.dashboardStatus.querySelector("[data-dashboard-retry]")?.addEventListener("click", () => requestDashboardSummary(true));
  } else {
    els.dashboardStatus.textContent = "";
  }
}

function clearDashboardValues() {
  ["dashTodaySales", "dashCustomersAttended", "dashConditionalsOverdue", "dashAlertsActive"].forEach((id) => {
    if (els[id]) els[id].textContent = "—";
  });
  ["dashMonthSales", "dashMonthProfit", "dashStockValue", "dashCreditOpen", "dashCashBalance", "dashCashIn", "dashCashOut", "dashPayablesOpen", "dashReceivableOpen"].forEach((id) => {
    if (els[id]) els[id].textContent = "—";
  });
  els.salesChart.innerHTML = "";
  els.paymentSummary.innerHTML = "";
  els.topProductsList.innerHTML = "";
  els.lowStockList.innerHTML = "";
}

async function requestDashboardSummary(force = false) {
  if (dashboardApiLoading && !force) return;
  let params;
  try {
    params = dashboardQuery();
  } catch (error) {
    setDashboardState("error", error.message);
    return;
  }
  const key = params.toString();
  if (!force && dashboardApiCache && dashboardApiKey === key) {
    renderDashboardFromSummary(dashboardApiCache);
    return;
  }
  const token = ++dashboardRequestToken;
  dashboardApiLoading = true;
  clearDashboardValues();
  setDashboardState("loading");
  try {
    const response = await fetch(`/api/dashboard?${params}`, { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (token !== dashboardRequestToken) return;
    if (handleUnauthorized(response, payload)) return;
    if (!response.ok || !payload.data) throw new Error(payload.error || "Não foi possível carregar o Dashboard.");
    dashboardApiCache = payload.data;
    dashboardApiKey = key;
    dashboardApiError = "";
    renderDashboardFromSummary(payload.data);
  } catch (error) {
    if (token !== dashboardRequestToken) return;
    dashboardApiCache = null;
    dashboardApiKey = "";
    dashboardApiError = error.message || "Não foi possível carregar o Dashboard.";
    clearDashboardValues();
    setDashboardState("error", dashboardApiError);
  } finally {
    if (token === dashboardRequestToken) dashboardApiLoading = false;
  }
}

function renderDashboardFromSummary(summary) {
  const metrics = summary.metrics || {};
  const admin = summary.profile === "admin";
  dashboardKnownToday = summary.today || dashboardKnownToday;
  document.querySelectorAll(".dashboard-admin-card").forEach((element) => element.hidden = !admin);
  document.querySelectorAll(".dashboard-operator-card").forEach((element) => element.hidden = admin);
  els.dashboardCards.classList.toggle("operator", !admin);
  els.dashboardFinanceSummary.hidden = !admin;
  els.dashTodaySales.textContent = String(metrics.todaySalesCount || 0);
  els.dashMonthSales.textContent = money.format(metrics.todayRevenue || 0);
  els.dashMonthProfit.textContent = money.format(metrics.monthProfit || 0);
  els.dashStockValue.textContent = money.format(metrics.stockValue || 0);
  els.dashCreditOpen.textContent = money.format(metrics.creditOpen || 0);
  els.dashCreditOpenCount.textContent = `${metrics.creditOpenCount || 0} parcela${metrics.creditOpenCount === 1 ? "" : "s"}`;
  els.dashCustomersAttended.textContent = String(metrics.customersAttended || 0);
  els.dashConditionalsOverdue.textContent = String(metrics.conditionalsOverdue || 0);
  els.dashAlertsActive.textContent = String(metrics.alertsActive || 0);
  els.dashAlertsUnread.textContent = `${metrics.alertsUnread || 0} não lido${metrics.alertsUnread === 1 ? "" : "s"}`;
  els.dashCashBalance.textContent = money.format(metrics.cashBalance || 0);
  els.dashCashIn.textContent = money.format(metrics.cashInToday || 0);
  els.dashCashOut.textContent = money.format(metrics.cashOutToday || 0);
  els.dashPayablesOpen.textContent = money.format(metrics.payablesOpen || 0);
  els.dashPayablesCount.textContent = `${metrics.payablesCount || 0} conta${metrics.payablesCount === 1 ? "" : "s"} em aberto`;
  els.dashReceivableOpen.textContent = money.format(metrics.cardReceivablesOpen || 0);
  els.dashReceivableCount.textContent = `${metrics.cardReceivablesCount || 0} recebíve${metrics.cardReceivablesCount === 1 ? "l" : "is"} em aberto`;
  els.topDateLabel.textContent = new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "full",
    timeZone: "America/Sao_Paulo",
  }).format(new Date(`${summary.today}T12:00:00-03:00`));
  renderSalesChartFromSummary(summary.salesChart || [], admin);
  renderPaymentSummaryFromSummary(summary.payments || {});
  renderTopBrandsFromSummary(summary.topBrands || []);
  renderStoppedProductsFromSummary(summary.stoppedProducts || [], admin);
  updateAlertBell({ unread: metrics.alertsUnread || 0 });
  setDashboardState("success");
}

function openDashboardAction(action) {
  if (action === "alerts") {
    openAlertsModal();
    return;
  }
  if (action === "sales-today") {
    activateTab("venda");
    activateSubtab("historico-vendas");
    els.saleHistoryStart.value = dashboardKnownToday;
    els.saleHistoryEnd.value = dashboardKnownToday;
    renderSaleHistory();
    return;
  }
  if (action === "conditionals") {
    activateTab("venda");
    activateSubtab("condicional");
    conditionalView = "list";
    renderConditionalPanels();
    return;
  }
  const destination = {
    stock: "estoque",
    credit: "crediario",
    cash: "caixa",
    payables: "contas",
    cards: "cartoes",
  }[action];
  if (destination) activateTab(destination);
}

function renderPaymentSummaryFromSummary(summary) {
  const colors = { cash: "#58bd4d", pix: "#2dbdc9", debit: "#ff841a", credit: "#9d54db", storeCredit: "#f45d8b" };
  const moneyValues = summary.valueType === "money";
  const rows = ["cash", "pix", "debit", "credit", "storeCredit"].map((method) => {
    const item = (summary.rows || []).find((row) => row.method === method) || {};
    return { method, ...item, chartValue: Number(item.chartValue || 0), color: colors[method] };
  });
  const activeRows = rows.filter((item) => item.chartValue > 0);
  let start = 0;
  const segments = activeRows.map((item) => {
    const end = start + Number(item.percent || 0);
    const segment = `${item.color} ${start}% ${end}%`;
    start = end;
    return segment;
  }).join(", ");
  const chartTotal = summary.chartTotal || 0;
  const emptyMessage = summary.hasNegativeValues
    ? "Sem valores positivos para exibir no gráfico."
    : "Nenhum pagamento no período selecionado.";
  els.paymentSummary.innerHTML = `
    <div class="payment-clean-head">
      <span class="payment-clean-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 3v9l7 4"></path><path d="M21 12a9 9 0 1 1-9-9"></path><path d="M12 3a9 9 0 0 1 9 9h-9V3Z"></path></svg></span>
      <div><h2>Vendas por forma de pagamento</h2><p>Distribuição no período selecionado.</p></div>
    </div>
    <div class="payment-clean-body">
      ${activeRows.length
        ? `<div class="payment-donut" style="background:conic-gradient(${segments})"><span>Total<strong>${moneyValues ? money.format(chartTotal) : chartTotal}</strong></span></div>`
        : `<div class="dashboard-chart-empty">${emptyMessage}</div>`}
      <div class="payment-clean-legend">${rows.map((item) => `
        <article style="--payment-color:${item.color}">
          <i></i>
          <div><strong>${paymentLabels[item.method]}</strong><span>${item.salesCount || 0} operação${item.salesCount === 1 ? "" : "ões"}</span></div>
          <div><b>${Number(item.percent || 0).toFixed(1)}%</b><span>${moneyValues ? `Líquido ${money.format(item.net || 0)}` : `${item.chartValue} operação${item.chartValue === 1 ? "" : "ões"}`}</span>${moneyValues && Number(item.returned || 0) > 0 ? `<small>Recebido ${money.format(item.gross || 0)} · Devolvido ${money.format(item.returned)}</small>` : ""}</div>
        </article>
      `).join("")}</div>
    </div>
    <div class="payment-total-strip">
      <span class="payment-total-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 20V10"></path><path d="M12 20V4"></path><path d="M19 20v-7"></path></svg></span>
      <div><strong>Total de vendas</strong><span>${summary.totalSales || 0} venda(s) realizada(s)</span></div>
      <div><strong>${moneyValues ? money.format(chartTotal) : chartTotal}</strong><span>${activeRows.length ? "100% do gráfico" : "Sem distribuição"}</span></div>
    </div>
  `;
}

function renderTopBrandsFromSummary(rows) {
  els.topProductsList.innerHTML = rows.length
    ? rows.map((item) => `<div class="summary-row brand-ranking-row"><b>${item.position}</b><span>${escapeHtml(item.name)}</span><strong>${item.qty} peça${item.qty === 1 ? "" : "s"}</strong></div>`).join("")
    : '<p class="empty">Sem vendas registradas.</p>';
}

function renderStoppedProductsFromSummary(rows, admin) {
  els.lowStockList.innerHTML = rows.length
    ? rows.map((item) => `<div class="summary-row danger-text"><span>${escapeHtml(item.name)} <small>${escapeHtml(item.code)}</small></span><strong>${item.days} dias</strong><small>Disponível ${item.availableStock}${admin ? ` · ${money.format(item.stoppedValue || 0)} parado` : ""}</small></div>`).join("")
    : '<p class="empty">Sem peças paradas acima de 90 dias.</p>';
}

function renderSalesChartFromSummary(rows, admin) {
  const hasData = rows.some((item) => Number(item.salesCount || 0) > 0 || Number(item.pieces || 0) > 0);
  if (!hasData) {
    els.salesChart.innerHTML = '<div class="dashboard-chart-empty">Nenhuma venda no período selecionado.</div>';
    return;
  }
  const valueOf = (item) => admin ? Number(item.total || 0) : Number(item.salesCount || 0);
  const max = Math.max(...rows.map(valueOf), 1);
  const width = 680;
  const height = 220;
  const pad = 22;
  const points = rows.map((item, index) => ({
    ...item,
    x: rows.length === 1 ? width / 2 : pad + (index / (rows.length - 1)) * (width - pad * 2),
    y: height - pad - (valueOf(item) / max) * (height - pad * 2),
  }));
  const path = points.map((point, index) => `${index ? "L" : "M"}${point.x.toFixed(1)} ${point.y.toFixed(1)}`).join(" ");
  els.salesChart.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Evolução de vendas por dia">
      <path class="line-area" d="${path} L${width - pad} ${height - pad} L${pad} ${height - pad} Z"></path>
      <path class="line-path" d="${path}"></path>
      ${points.map((point) => {
        const financial = admin ? `\nTotal líquido: ${money.format(point.total || 0)}` : "";
        const tooltip = `Vendas por dia\n${formatDate(point.date)}${financial}\nVendas: ${point.salesCount || 0}\nPeças: ${point.pieces || 0}`;
        return `<g class="line-point-group"><circle class="line-point" cx="${point.x.toFixed(1)}" cy="${point.y.toFixed(1)}" r="3"></circle><circle class="line-hit-area" cx="${point.x.toFixed(1)}" cy="${point.y.toFixed(1)}" r="11" tabindex="0" data-tooltip="${escapeHtml(tooltip)}"></circle></g>`;
      }).join("")}
      <text x="${pad}" y="${height - 4}">${formatDate(rows[0].date)}</text>
      <text x="${width - pad}" y="${height - 4}" text-anchor="end">${formatDate(rows.at(-1).date)}</text>
    </svg>
  `;
  bindChartTooltips(els.salesChart);
}

function updateAlertBell(summary = {}) {
  const unread = Number(summary.unread || 0);
  els.alertBellCount.textContent = unread > 99 ? "99+" : String(unread);
  els.alertBellCount.hidden = unread <= 0;
  els.alertBellButton.classList.toggle("has-alerts", unread > 0);
}

function openAlertsModal() {
  alertsPage = 1;
  els.alertsModal.hidden = false;
  loadAlerts(true);
}

function closeAlertsModal() {
  els.alertsModal.hidden = true;
}

function alertsQuery() {
  const params = new URLSearchParams({
    page: String(alertsPage),
    pageSize: "10",
  });
  if (els.alertsSearch.value.trim()) params.set("search", els.alertsSearch.value.trim());
  if (els.alertsPriority.value) params.set("priority", els.alertsPriority.value);
  if (els.alertsModule.value) params.set("module", els.alertsModule.value);
  if (els.alertsState.value) params.set("state", els.alertsState.value);
  return params;
}

async function loadAlerts(force = false) {
  if (!session || !BACKEND_ENABLED || alertsLoading) return;
  if (!force && alertsLoaded) return;
  alertsLoading = true;
  if (!els.alertsModal.hidden) {
    els.alertsFeedback.textContent = "Carregando alertas...";
    els.alertsList.innerHTML = "";
  }
  try {
    const response = await fetch(`/api/alerts?${alertsQuery()}`, { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (handleUnauthorized(response, payload)) return;
    if (!response.ok || !payload.data) throw new Error(payload.error || "Não foi possível carregar os alertas.");
    alertsData = payload.data;
    alertsLoaded = true;
    updateAlertBell(alertsData.summary);
    renderAlerts();
  } catch (error) {
    if (!els.alertsModal.hidden) {
      els.alertsFeedback.innerHTML = `${escapeHtml(error.message)} <button class="ghost" type="button" data-alert-retry>Tentar novamente</button>`;
      els.alertsFeedback.querySelector("[data-alert-retry]")?.addEventListener("click", () => loadAlerts(true));
    }
  } finally {
    alertsLoading = false;
  }
}

function renderAlerts() {
  if (els.alertsModal.hidden) return;
  const items = alertsData.items || [];
  const pagination = alertsData.pagination || {};
  const summary = alertsData.summary || {};
  els.alertsFeedback.textContent = `${summary.active || 0} ativo(s) · ${summary.unread || 0} não lido(s) · ${summary.critical || 0} crítico(s)`;
  els.alertsList.innerHTML = items.length
    ? items.map((item) => `
      <article class="alert-row ${item.read ? "read" : "unread"} ${item.pinned ? "pinned" : ""}" data-alert-id="${escapeHtml(item.id)}">
        <span class="alert-priority ${escapeHtml(item.priority)}">${item.priority === "critical" ? "Crítico" : "Atenção"}</span>
        <div><strong>${escapeHtml(item.title)}</strong><p>${escapeHtml(item.message)}</p><small>${escapeHtml(item.moduleLabel)} · ${item.days || 0} dia(s) · ${item.amount != null ? money.format(item.amount) : `${item.count || 0} item(ns)`}</small></div>
        <div class="alert-row-actions">
          <button class="icon-button" type="button" data-alert-pin="${escapeHtml(item.id)}" title="${item.pinned ? "Desafixar" : "Fixar"}" aria-label="${item.pinned ? "Desafixar" : "Fixar"}">${item.pinned ? "★" : "☆"}</button>
          <button class="icon-button" type="button" data-alert-read="${escapeHtml(item.id)}" title="${item.read ? "Marcar como não lido" : "Marcar como lido"}" aria-label="${item.read ? "Marcar como não lido" : "Marcar como lido"}">${item.read ? "○" : "●"}</button>
          <button class="ghost" type="button" data-alert-open="${escapeHtml(item.id)}">${escapeHtml(item.action?.label || "Abrir")}</button>
        </div>
      </article>
    `).join("")
    : '<div class="alerts-empty">Nenhum alerta encontrado.</div>';
  els.alertsList.querySelectorAll("[data-alert-open]").forEach((buttonElement) => {
    buttonElement.addEventListener("click", () => openAlertAction(buttonElement.dataset.alertOpen));
  });
  els.alertsList.querySelectorAll("[data-alert-pin]").forEach((buttonElement) => {
    buttonElement.addEventListener("click", () => toggleAlertPin(buttonElement.dataset.alertPin));
  });
  els.alertsList.querySelectorAll("[data-alert-read]").forEach((buttonElement) => {
    buttonElement.addEventListener("click", () => toggleAlertRead(buttonElement.dataset.alertRead));
  });
  const totalPages = Number(pagination.totalPages || 1);
  const currentPage = Number(pagination.page || alertsPage);
  els.alertsPagination.innerHTML = `
    <button class="ghost" type="button" data-alert-page="${currentPage - 1}" ${currentPage <= 1 ? "disabled" : ""}>Anterior</button>
    <span>Página ${currentPage} de ${totalPages}</span>
    <button class="ghost" type="button" data-alert-page="${currentPage + 1}" ${currentPage >= totalPages ? "disabled" : ""}>Próxima</button>
  `;
  els.alertsPagination.querySelectorAll("[data-alert-page]").forEach((buttonElement) => {
    buttonElement.addEventListener("click", () => {
      if (buttonElement.disabled) return;
      alertsPage = Number(buttonElement.dataset.alertPage);
      loadAlerts(true);
    });
  });
}

async function updateAlertState(alertId, operation, value) {
  const response = await fetch(`/api/alerts/${encodeURIComponent(alertId)}/${operation}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ [operation === "read" ? "read" : "pinned"]: value }),
  });
  const payload = await response.json().catch(() => ({}));
  if (handleUnauthorized(response, payload)) return null;
  if (!response.ok) throw new Error(payload.error || "Não foi possível atualizar o alerta.");
  alertsLoaded = false;
  await loadAlerts(true);
  invalidateDashboardCache();
  renderDashboard();
  return payload.data;
}

async function toggleAlertPin(alertId) {
  const item = (alertsData.items || []).find((entry) => entry.id === alertId);
  if (!item) return;
  try {
    await updateAlertState(alertId, "pin", !item.pinned);
  } catch (error) {
    els.alertsFeedback.textContent = error.message;
  }
}

async function toggleAlertRead(alertId) {
  const item = (alertsData.items || []).find((entry) => entry.id === alertId);
  if (!item) return;
  try {
    await updateAlertState(alertId, "read", !item.read);
  } catch (error) {
    els.alertsFeedback.textContent = error.message;
  }
}

async function markAllAlertsRead() {
  try {
    const response = await fetch("/api/alerts/read-all", { method: "POST" });
    const payload = await response.json().catch(() => ({}));
    if (handleUnauthorized(response, payload)) return;
    if (!response.ok) throw new Error(payload.error || "Não foi possível marcar os alertas.");
    alertsLoaded = false;
    await loadAlerts(true);
    invalidateDashboardCache();
    renderDashboard();
  } catch (error) {
    els.alertsFeedback.textContent = error.message;
  }
}

async function openAlertAction(alertId) {
  const item = (alertsData.items || []).find((entry) => entry.id === alertId);
  if (!item) return;
  try {
    if (!item.read) await updateAlertState(alertId, "read", true);
  } catch (error) {
    els.alertsFeedback.textContent = error.message;
    return;
  }
  closeAlertsModal();
  const action = item.action || {};
  if (action.tab) activateTab(action.tab);
  if (action.subtab) activateSubtab(action.subtab);
  if (action.customerId && els.creditCustomerSearch) {
    els.creditCustomerSearch.value = item.customerName || item.entityNumber || "";
    selectedCreditCustomerId = action.customerId;
    renderCreditCustomers();
  }
  if (action.payableId && els.payableSearch) {
    els.payableSearch.value = item.entityNumber || action.payableId;
    renderPayables();
  }
  if (action.productId && els.stockSearch) {
    els.stockSearch.value = item.entityNumber || "";
    renderStock();
  }
  if (action.conditionalId) {
    selectedConditionalId = action.conditionalId;
    conditionalView = "detail";
    renderConditionalPanels();
  }
}

const reportFilterOptions = {
  method: [["", "Todas"], ["cash", "Dinheiro"], ["pix", "PIX"], ["debit", "Débito"], ["credit", "Crédito"], ["storeCredit", "Crediário"]],
  direction: [["", "Todas"], ["in", "Entradas"], ["out", "Saídas"]],
  dateType: [["due", "Vencimento"], ["issue", "Emissão"]],
  stockStatus: [["", "Todos"], ["with_stock", "Com estoque disponível"], ["last_unit", "Última unidade"], ["zero", "Sem estoque disponível"]],
};

const reportStatusOptions = {
  sales: [["", "Todas"], ["completed", "Concluídas"], ["partial", "Parcialmente devolvidas"], ["returned", "Devolvidas"], ["cancelled", "Canceladas"]],
  "store-credit": [["", "Todas"], ["open", "Em dia"], ["overdue", "Atrasadas"], ["paid", "Quitadas"], ["cancelled", "Canceladas"]],
  payables: [["", "Todas"], ["open", "A vencer"], ["today", "Vencem hoje"], ["overdue", "Vencidas"], ["paid", "Quitadas"], ["cancelled", "Canceladas"]],
  conditionals: [["", "Todos"], ["open", "Em aberto"], ["overdue", "Atrasados"], ["finalized", "Finalizados"], ["cancelled", "Cancelados"]],
};

function renderReports() {
  if (!session || !els.relatorios.classList.contains("active")) return;
  if (!reportCatalogLoaded) {
    loadReportCatalog();
    return;
  }
  renderReportNavigation();
  renderReportData();
}

async function loadReportCatalog(force = false) {
  if (!BACKEND_ENABLED || !session || reportCatalogLoading) return;
  if (reportCatalogLoaded && !force) {
    renderReportNavigation();
    renderReportFilterControls();
    if (!reportCurrentData) loadCurrentReport();
    return;
  }
  reportCatalogLoading = true;
  reportError = "";
  renderReportLoading("Carregando relatórios disponíveis...");
  try {
    const response = await fetch("/api/reports/catalog", { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      throw new Error(payload.error || "Não foi possível carregar os relatórios.");
    }
    reportCatalog = Array.isArray(payload.data) ? payload.data : [];
    reportCatalogLoaded = true;
    if (!reportCatalog.some((item) => item.key === reportCurrentKey)) {
      reportCurrentKey = reportCatalog[0]?.key || "";
    }
    renderReportNavigation();
    renderReportFilterControls();
    updateReportPeriodControls();
    await loadCurrentReport(true);
  } catch (error) {
    console.warn(error);
    reportError = error.message || "Não foi possível carregar os relatórios.";
    renderReportError();
  } finally {
    reportCatalogLoading = false;
  }
}

function currentReportDefinition() {
  return reportCatalog.find((item) => item.key === reportCurrentKey) || null;
}

function renderReportNavigation() {
  els.reportType.innerHTML = reportCatalog.map((item) => `
    <option value="${escapeHtml(item.key)}"${item.key === reportCurrentKey ? " selected" : ""}>${escapeHtml(item.title.replace(/^Relatório de /, ""))}</option>
  `).join("");
  els.reportNavigation.innerHTML = reportCatalog.map((item, index) => `
    <button class="${item.key === reportCurrentKey ? "active" : ""}" type="button" data-report-key="${escapeHtml(item.key)}">
      <span>${String(index + 1).padStart(2, "0")}</span>
      <strong>${escapeHtml(item.title.replace(/^Relatório de /, ""))}</strong>
    </button>
  `).join("");
}

function selectReport(key) {
  if (!reportCatalog.some((item) => item.key === key)) return;
  reportCurrentKey = key;
  reportCurrentData = null;
  reportCurrentRequestKey = "";
  reportError = "";
  renderReportNavigation();
  renderReportFilterControls();
  updateReportPeriodControls();
  loadCurrentReport(true);
}

function reportFilterControl(filter) {
  const options = filter.key === "status"
    ? (reportStatusOptions[reportCurrentKey] || [["", "Todas"]])
    : reportFilterOptions[filter.key];
  if (options) {
    return `
      <label class="field">${escapeHtml(filter.label)}
        <select data-report-filter="${escapeHtml(filter.key)}">
          ${options.map(([value, label]) => `<option value="${escapeHtml(value)}">${escapeHtml(label)}</option>`).join("")}
        </select>
      </label>
    `;
  }
  const placeholders = {
    search: "Nome, código ou identificação...",
    customer: "Nome ou CPF...",
    user: "Nome do usuário...",
    product: "Nome ou código...",
    brand: "Nome da marca...",
    category: "Nome da categoria...",
    expenseCategory: "Tipo da despesa...",
    supplier: "Nome do fornecedor...",
    size: "Tamanho...",
    color: "Cor...",
  };
  return `
    <label class="field">${escapeHtml(filter.label)}
      <input data-report-filter="${escapeHtml(filter.key)}" type="search" maxlength="160" placeholder="${escapeHtml(placeholders[filter.key] || "Filtrar...")}">
    </label>
  `;
}

function renderReportFilterControls() {
  const definition = currentReportDefinition();
  els.reportFilters.innerHTML = (definition?.filters || []).map(reportFilterControl).join("");
  const supportsPeriod = Boolean(definition?.period);
  els.reportPeriod.disabled = !supportsPeriod;
  els.reportPeriod.closest(".field").hidden = !supportsPeriod;
  els.reportExportPdf.hidden = !(definition?.formats || []).includes("pdf");
  els.reportExportXlsx.hidden = !(definition?.formats || []).includes("xlsx");
}

function updateReportPeriodControls() {
  const definition = currentReportDefinition();
  const custom = Boolean(definition?.period && els.reportPeriod.value === "custom");
  els.reportCustomPeriod.hidden = !custom;
  els.reportStart.disabled = !custom;
  els.reportEnd.disabled = !custom;
}

function collectReportParams(page = 1) {
  const definition = currentReportDefinition();
  const params = new URLSearchParams();
  if (definition?.period) {
    params.set("period", els.reportPeriod.value || "30days");
    if (els.reportPeriod.value === "custom") {
      params.set("start", els.reportStart.value);
      params.set("end", els.reportEnd.value);
    }
  }
  els.reportFilters.querySelectorAll("[data-report-filter]").forEach((input) => {
    if (input.value) params.set(input.dataset.reportFilter, input.value);
  });
  params.set("page", String(page));
  params.set("pageSize", "20");
  return params;
}

async function loadCurrentReport(force = false, page = 1) {
  if (!reportCatalogLoaded || !reportCurrentKey || reportLoading) return;
  const params = collectReportParams(page);
  const requestKey = `${session?.id || ""}:${session?.role || ""}:${reportCurrentKey}:${params}`;
  if (!force && reportCurrentData && reportCurrentRequestKey === requestKey) {
    renderReportData();
    return;
  }
  reportLoading = true;
  reportError = "";
  reportCurrentData = null;
  const token = ++reportRequestToken;
  renderReportLoading("Consultando dados do relatório...");
  try {
    const response = await fetch(`/api/reports/${encodeURIComponent(reportCurrentKey)}?${params}`, { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (token !== reportRequestToken) return;
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) return;
      throw new Error(payload.error || "Não foi possível gerar o relatório.");
    }
    reportCurrentData = payload.data || null;
    reportCurrentRequestKey = requestKey;
    reportLoading = false;
    renderReportData();
  } catch (error) {
    if (token !== reportRequestToken) return;
    console.warn(error);
    reportError = error.message || "Não foi possível gerar o relatório.";
    renderReportError();
  } finally {
    if (token === reportRequestToken) reportLoading = false;
  }
}

function renderReportLoading(message) {
  els.reportFeedback.className = "report-feedback loading";
  els.reportFeedback.innerHTML = `<span class="report-spinner" aria-hidden="true"></span><strong>${escapeHtml(message)}</strong>`;
  els.reportSummary.innerHTML = Array.from({ length: 4 }, () => '<div class="report-summary-card skeleton"></div>').join("");
  els.reportTableHead.innerHTML = "";
  els.reportTableBody.innerHTML = Array.from({ length: 6 }, () => '<tr class="report-skeleton-row"><td colspan="12"></td></tr>').join("");
  els.reportPagination.innerHTML = "";
}

function renderReportError() {
  els.reportFeedback.className = "report-feedback error";
  els.reportFeedback.innerHTML = `<div><strong>Não foi possível carregar o relatório.</strong><span>${escapeHtml(reportError)}</span></div><button class="ghost" type="button" data-report-retry>Tentar novamente</button>`;
  els.reportSummary.innerHTML = "";
  els.reportTableHead.innerHTML = "";
  els.reportTableBody.innerHTML = "";
  els.reportPagination.innerHTML = "";
}

function reportDisplayValue(value, type) {
  if (value === null || value === undefined || value === "") return "-";
  if (type === "money") return money.format(Number(value || 0));
  if (type === "percent") return `${Number(value || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}%`;
  if (type === "integer") return Number(value || 0).toLocaleString("pt-BR");
  if (type === "boolean") return value ? "Sim" : "Não";
  return String(value);
}

function renderReportData() {
  if (reportLoading) return;
  if (reportError) {
    renderReportError();
    return;
  }
  const data = reportCurrentData;
  if (!data) return;
  els.reportFeedback.className = "report-feedback";
  els.reportFeedback.innerHTML = "";
  els.reportResultTitle.textContent = data.title || "Relatório";
  const period = data.metadata?.period || {};
  els.reportResultMeta.textContent = period.start ? `${formatDate(period.start)} a ${formatDate(period.end)}` : "Posição atual";
  els.reportSummary.innerHTML = (data.summary || []).map((item) => `
    <article class="report-summary-card">
      <span>${escapeHtml(item.label || "")}</span>
      <strong>${escapeHtml(reportDisplayValue(item.value, item.type))}</strong>
    </article>
  `).join("");
  const columns = data.columns || [];
  els.reportTableHead.innerHTML = `<tr>${columns.map((column) => `<th>${escapeHtml(column.label || "")}</th>`).join("")}${reportCurrentKey === "sales" ? "<th>Ações</th>" : ""}</tr>`;
  const rows = data.rows || [];
  if (!rows.length) {
    els.reportTableBody.innerHTML = `<tr><td colspan="${columns.length + (reportCurrentKey === "sales" ? 1 : 0)}"><div class="report-empty"><strong>Nenhum registro encontrado.</strong><span>Ajuste o período ou os filtros para consultar outros dados.</span></div></td></tr>`;
  } else {
    els.reportTableBody.innerHTML = rows.map((row) => `
      <tr>
        ${columns.map((column) => `<td data-label="${escapeHtml(column.label || "")}">${escapeHtml(reportDisplayValue(row[column.key], column.type))}</td>`).join("")}
        ${reportCurrentKey === "sales" ? `<td data-label="Ações"><button class="icon-button report-detail-button" type="button" data-report-sale="${escapeHtml(row.id)}" title="Visualizar venda" aria-label="Visualizar venda">⌕</button></td>` : ""}
      </tr>
    `).join("");
  }
  renderReportPagination(data.pagination || {});
}

function renderReportPagination(pagination) {
  const page = Number(pagination.page || 1);
  const pages = Number(pagination.pages || 0);
  if (pages <= 1) {
    els.reportPagination.innerHTML = `<span>${Number(pagination.total || 0).toLocaleString("pt-BR")} registro(s)</span>`;
    return;
  }
  const pageButtons = [];
  for (let current = Math.max(1, page - 2); current <= Math.min(pages, page + 2); current += 1) {
    pageButtons.push(`<button class="${current === page ? "active" : ""}" type="button" data-report-page="${current}">${current}</button>`);
  }
  els.reportPagination.innerHTML = `
    <span>${Number(pagination.total || 0).toLocaleString("pt-BR")} registro(s)</span>
    <div>
      <button type="button" data-report-page="${page - 1}" ${page <= 1 ? "disabled" : ""}>Anterior</button>
      ${pageButtons.join("")}
      <button type="button" data-report-page="${page + 1}" ${page >= pages ? "disabled" : ""}>Próximo</button>
    </div>
  `;
}

async function exportCurrentReport(format) {
  const definition = currentReportDefinition();
  if (!definition || reportExporting || !(definition.formats || []).includes(format)) return;
  reportExporting = true;
  const button = format === "pdf" ? els.reportExportPdf : els.reportExportXlsx;
  const original = button.textContent;
  button.disabled = true;
  button.textContent = "Gerando...";
  try {
    const params = collectReportParams();
    params.delete("page");
    params.delete("pageSize");
    params.set("format", format);
    const response = await fetch(`/api/reports/${encodeURIComponent(reportCurrentKey)}/export?${params}`, { cache: "no-store" });
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      if (handleUnauthorized(response, payload)) return;
      throw new Error(payload.error || "Não foi possível exportar o relatório.");
    }
    const blob = await response.blob();
    const disposition = response.headers.get("Content-Disposition") || "";
    const encodedName = disposition.match(/filename\*=UTF-8''([^;]+)/i)?.[1];
    const simpleName = disposition.match(/filename="?([^";]+)"?/i)?.[1];
    const filename = encodedName ? decodeURIComponent(encodedName) : (simpleName || `mova-sports-${reportCurrentKey}.${format}`);
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  } catch (error) {
    console.warn(error);
    alert(error.message || "Não foi possível exportar o relatório.");
  } finally {
    reportExporting = false;
    button.disabled = false;
    button.textContent = original;
  }
}

async function openReportSaleDetails(saleId) {
  els.reportDetailTitle.textContent = "Detalhes da venda";
  els.reportDetailBody.innerHTML = '<div class="report-detail-loading">Carregando detalhes...</div>';
  els.reportDetailModal.hidden = false;
  try {
    const response = await fetch(`/api/reports/sales/${encodeURIComponent(saleId)}/details`, { cache: "no-store" });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (handleUnauthorized(response, payload)) {
        closeReportDetail();
        return;
      }
      throw new Error(payload.error || "Não foi possível carregar a venda.");
    }
    const sale = payload.data || {};
    els.reportDetailTitle.textContent = sale.saleNumber ? `Venda VENDA${String(sale.saleNumber).padStart(3, "0")}` : `Venda ${sale.id || ""}`;
    els.reportDetailBody.innerHTML = `
      <div class="report-detail-meta">
        <span><b>Cliente</b>${escapeHtml(sale.customerName || "Venda simples")}</span>
        <span><b>Data</b>${escapeHtml(formatStoreDateTime(sale.createdAt))}</span>
        <span><b>Usuário</b>${escapeHtml(sale.userName || "Não informado")}</span>
        <span><b>Situação</b>${escapeHtml(sale.status || "-")}</span>
      </div>
      <div class="report-detail-items">
        ${(sale.items || []).map((item) => `<div><span>${Number(item.quantity || 0)}x ${escapeHtml(item.name || "-")}<small>${escapeHtml([item.barcode, item.size, item.color, item.brand].filter(Boolean).join(" | "))}</small></span><strong>${money.format(Number(item.netTotal || 0))}</strong></div>`).join("") || "<p>Nenhum item registrado.</p>"}
      </div>
      <div class="report-detail-total"><span>Total da venda</span><strong>${money.format(Number(sale.total || 0))}</strong></div>
      <div class="report-detail-payments">
        ${(sale.payments || []).map((item) => `<span>${escapeHtml(paymentLabels[item.method] || item.method || "-")}<b>${money.format(Number(item.amount || 0))}</b></span>`).join("") || "<span>Pagamento não informado</span>"}
      </div>
    `;
  } catch (error) {
    console.warn(error);
    els.reportDetailBody.innerHTML = `<div class="report-empty"><strong>Não foi possível carregar os detalhes.</strong><span>${escapeHtml(error.message || "")}</span></div>`;
  }
}

function closeReportDetail() {
  els.reportDetailModal.hidden = true;
  els.reportDetailBody.innerHTML = "";
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

async function importSystemData() {
  if (!BACKEND_ENABLED || !canImportOrResetData()) return;
  const file = els.importDataFile.files?.[0];
  const confirmation = els.importDataConfirmation.value.trim();
  if (!file) return alert("Selecione um arquivo JSON exportado pelo sistema.");
  if (confirmation !== "RESTAURAR") return alert("Digite RESTAURAR para confirmar a importação.");
  const accepted = confirm("Esta ação substitui os dados atuais do sistema pelo arquivo selecionado. Deseja continuar?");
  if (!accepted) return;
  els.importDataButton.disabled = true;
  els.importDataStatus.textContent = "Restaurando dados...";
  try {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("confirmation", confirmation);
    const response = await fetch("/api/import", { method: "POST", body: formData });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      alert(payload.error || "Não foi possível restaurar os dados.");
      els.importDataStatus.textContent = payload.error || "Falha na restauração.";
      return;
    }
    const data = payload.data || {};
    els.importDataFile.value = "";
    els.importDataConfirmation.value = "";
    els.importDataStatus.textContent = `Restauração concluída: ${data.products || 0} produtos, ${data.customers || 0} clientes e ${data.sales || 0} vendas.`;
    backupsLoaded = false;
    databaseStatusLoaded = false;
    auditLogsLoaded = false;
    await syncFromServer();
    await loadDatabaseStatus(true);
    await loadAuditLogs(true);
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para restaurar os dados.");
    els.importDataStatus.textContent = "Falha de conexão durante a restauração.";
  } finally {
    els.importDataButton.disabled = false;
  }
}

async function resetSystemData() {
  if (!BACKEND_ENABLED || !canImportOrResetData()) return;
  const confirmation = els.resetDataConfirmation.value.trim();
  if (confirmation !== "ZERAR") return alert("Digite ZERAR para confirmar a limpeza do sistema.");
  const accepted = confirm("Esta ação apaga cadastros, vendas, caixa e financeiro. Usuários serão mantidos. Deseja continuar?");
  if (!accepted) return;
  els.resetDataButton.disabled = true;
  els.resetDataStatus.textContent = "Exportando dados atuais antes de zerar...";
  try {
    await exportSystemData();
    els.resetDataStatus.textContent = "Zerando sistema...";
    const response = await fetch("/api/reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ confirmation }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      alert(payload.error || "Não foi possível zerar o sistema.");
      els.resetDataStatus.textContent = payload.error || "Falha ao zerar sistema.";
      return;
    }
    els.resetDataConfirmation.value = "";
    els.resetDataStatus.textContent = "Sistema zerado. Usuários e auditoria foram preservados.";
    backupsLoaded = false;
    databaseStatusLoaded = false;
    auditLogsLoaded = false;
    selectedSaleHistoryKey = "";
    cart = [];
    await syncFromServer();
    await loadDatabaseStatus(true);
    await loadAuditLogs(true);
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para zerar o sistema.");
    els.resetDataStatus.textContent = "Falha de conexão durante a limpeza.";
  } finally {
    els.resetDataButton.disabled = false;
  }
}

async function changePassword(event) {
  event.preventDefault();
  if (!BACKEND_ENABLED) return alert("Alteração de senha exige servidor ativo.");
  const currentPassword = els.currentPassword.value;
  const newPassword = els.newPassword.value;
  const confirmPassword = els.confirmPassword.value;
  if (!currentPassword || !newPassword) return alert("Informe a senha atual e a nova senha.");
  if (newPassword !== confirmPassword) return alert("A confirmação da senha não confere.");
  els.changePasswordStatus.textContent = "Alterando senha...";
  const submitButton = els.changePasswordForm.querySelector("button[type='submit']");
  submitButton.disabled = true;
  try {
    const response = await fetch("/api/me/password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ currentPassword, newPassword, confirmPassword }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      alert(payload.error || "Não foi possível alterar a senha.");
      els.changePasswordStatus.textContent = payload.error || "Falha ao alterar senha.";
      return;
    }
    els.changePasswordForm.reset();
    els.changePasswordStatus.textContent = "Senha alterada com sucesso.";
    await loadAuditLogs(true);
  } catch (error) {
    console.warn(error);
    alert("Não foi possível conectar ao servidor para alterar a senha.");
    els.changePasswordStatus.textContent = "Falha de conexão.";
  } finally {
    submitButton.disabled = false;
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
    reset: "Zerou sistema",
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
  if (item.openAmount !== undefined && item.openAmount !== null) {
    return Math.max(0, round(item.openAmount));
  }
  return Math.max(
    0,
    round(
      Number(item.amount || 0)
        - Number(item.received || 0)
        - Number(item.discountTotal || 0),
    ),
  );
}

function payableTotalDue(item) {
  const charges = Number(item.interest || 0) || Number(item.fine || 0)
    ? Number(item.interest || 0) + Number(item.fine || 0)
    : Number(item.fee || 0);
  return Math.max(0, round(
    Number(item.amount || 0)
    + charges
    - Number(item.discount || 0),
  ));
}

function payableBalance(item) {
  if (item.status === "cancelled") return 0;
  if (item.openAmount !== null && item.openAmount !== undefined) {
    return Math.max(0, round(Number(item.openAmount || 0)));
  }
  return Math.max(0, round(
    payableTotalDue(item)
    - Number(item.paidAmount || 0)
    - Number(item.supplierAdjustments || 0)
  ));
}

function payableStatus(item) {
  if (item.status === "cancelled") return "cancelled";
  if (item.status === "paid" || payableBalance(item) <= 0.01) return "paid";
  if (item.dueDate === todayIso) return "today";
  if (item.dueDate < todayIso) return "overdue";
  return "pending";
}

function findCustomerByName(name) {
  return db.customers.find((customer) => (
    !customer.isDefault
    && customer.status !== "deactivated"
    && normalize(customer.name) === normalize(name)
  ));
}

function findActiveCustomerByName(name) {
  const customer = findCustomerByName(name);
  return customer?.status === "active" ? customer : undefined;
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

function formatStoreDateTime(value) {
  if (!value) return "-";
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? "-"
    : new Intl.DateTimeFormat("pt-BR", {
      dateStyle: "short",
      timeStyle: "short",
      timeZone: "America/Sao_Paulo",
    }).format(date);
}

function storeOperationalDateKey(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: "America/Sao_Paulo",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(date);
  const values = Object.fromEntries(parts.map((part) => [part.type, part.value]));
  return `${values.year}-${values.month}-${values.day}`;
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
