/*
global
alertify: false
csrf_token: false
documentationUrl: false
filteringPanel: false
formProperties: false
jsPanel: false
NProgress: false
page: false
panelCode: false
properties: false
propertyTypes: false
saveService: false
saveWorkflow: false
table: false
type: false
*/

const currentUrl = window.location.href.split("#")[0].split("?")[0];

const panelSize = {
  add_jobs: "800 500",
  cluster: "700 200",
  connection: "400 500",
  configuration: "700 700",
  configuration_filtering: "700 600",
  database_deletion: "700 400",
  database_migration: "700 300",
  device: "700 500",
  device_automation: "800 500",
  device_filtering: "700 600",
  event_filtering: "700 400",
  excel_import: "400 150",
  excel_export: "400 150",
  git: "900 200",
  google_earth_export: "700 200",
  instance_deletion: "400 130",
  librenms: "700 250",
  link: "700 400",
  link_filtering: "700 600",
  log_filtering: "700 350",
  notifications: "1100 400",
  netbox: "700 250",
  opennms: "700 300",
  pool: "800 600",
  pool_filtering: "700 500",
  pool_objects: "700 550",
  restart_workflow: "600 200",
  results: "1000 700",
  server: "600 250",
  server_filtering: "700 450",
  service: "1000 600",
  service_filtering: "1000 600",
  ssh: "700 200",
  task: "900 500",
  task_filtering: "900 650",
  user: "600 300",
  user_filtering: "700 250",
  view: "700 300",
  workflow: "1000 600",
  workflow_filtering: "1000 600",
};

const panelName = {
  add_jobs: "Add jobs",
  configuration: "Configuration",
  configuration_filtering: "Configuration Filtering",
  connection: "Connect to device",
  database_deletion: "Database Deletion",
  database_migration: "Database Migration",
  device_automation: "Device Automation",
  device_filtering: "Device Filtering",
  event_filtering: "Event Filtering",
  excel_export: "Export Topology as an Excel file",
  server_filtering: "Server Filtering",
  link_filtering: "Link Filtering",
  log_filtering: "Log Filtering",
  pool_filtering: "Pool Filtering",
  restart_workflow: "Restart Workflow",
  service_filtering: "Service Filtering",
  task_filtering: "Task Filtering",
  user_filtering: "User Filtering",
  workflow_filtering: "Workflow Filtering",
};

let topZ = 1000;

/**
 * Update link to the docs.
 * @param {url} url - URL pointing to the right page of the docs.
 */
// eslint-disable-next-line
function doc(page) {
  let endpoint = {
    administration: "administration/index.html",
    calendar: "events/tasks.html",
    dashboard: "base/introduction.html",
    "table/configuration": "inventory/configuration_management.html",
    "table/device": "inventory/objects.html",
    "table/event": "events/index.html",
    "table/link": "inventory/objects.html",
    "table/log": "events/logs.html",
    "table/pool": "inventory/pool_management.html",
    "table/server": "administration/index.html",
    "table/service": "services/index.html",
    "table/task": "events/tasks.html",
    "table/user": "administration/index.html",
    "table/workflow": "workflows/index.html",
    view: "views/geographical_view.html",
    workflow_builder: "workflows/index.html",
  }[page];
  $("#doc-link").attr("href", `${documentationUrl}${endpoint}`);
}

$.ajaxSetup({
  beforeSend: function(xhr, settings) {
    if (
      !/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) &&
      !this.crossDomain
    ) {
      xhr.setRequestHeader("X-CSRFToken", csrf_token);
    }
  },
});

/**
 * Open new tab at the provided URL.
 * @param {url} url - URL.
 */
// eslint-disable-next-line
function openUrl(url) {
  let win = window.open(url, "_blank");
  win.focus();
}

/**
 * Process results.
 * @param {callback} callback - Callback function.
 * @param {results} results - Results.
 */
function processResults(callback, results) {
  if (results === false) {
    alertify.notify("HTTP Error 403 – Forbidden", "error", 5);
  } else if (results && results.error) {
    alertify.notify(results.error, "error", 5);
  } else if (results && results.invalid_form) {
    for (const [field, error] of Object.entries(results.errors)) {
      alertify.notify(`Wrong input for "${field}": ${error}`, "error", 20);
    }
  } else {
    callback(results);
  }
}

/**
 * jQuery Ajax Call.
 * @param {url} url - Url.
 * @param {callback} callback - Function to process results.
 */
function call(url, callback) {
  $.ajax({
    type: "POST",
    url: url,
    success: function(results) {
      processResults(callback, results);
    },
  });
}

/**
 * jQuery Ajax Form Call.
 * @param {string} url - Url.
 * @param {string} form - Form ID.
 * @param {function} callback - Function to process results.
 */
function fCall(url, form, callback) {
  if (
    $(form)
      .parsley()
      .validate()
  ) {
    $.ajax({
      type: "POST",
      url: url,
      data: $(form).serialize(),
      success: function(results) {
        processResults(callback, results);
      },
    });
  }
}

/**
 * Serialize form for table filtering.
 * @param {string} form - Form ID.
 * @return {object} Serialized form.
 */
function serializeForm(form) {
  const data = JSON.parse(JSON.stringify($(form).serializeArray()));
  let result = { pools: [] };
  data.forEach((property) => {
    if (property.name == "pools") {
      result.pools.push(property.value);
    } else {
      result[property.name] = property.value;
    }
  });
  return result;
}

/**
 * Delete object.
 * @param {type} type - Node or link.
 * @param {id} id - Id of the object to delete.
 */
// eslint-disable-next-line
function deleteInstance(type, id) {
  call(`/delete_instance/${type}/${id}`, function(result) {
    $(`#instance_deletion-${id}`).remove();
    table
      .row($(`#${id}`))
      .remove()
      .draw(false);
    alertify.notify(
      `${type.toUpperCase()} '${result.name}' deleted.`,
      "error",
      5
    );
  });
}

/**
 * Configure panel.
 * @param {id} id - Instance ID.
 * @param {contentSize} contentSize - Content size.
 * @param {url} url - URL to fetch the content from.
 * @param {processing} processing - Function once panel is loaded.
 */
// eslint-disable-next-line
function createPanel(name, title, id, processing, type, duplicate) {
  const panelId = id ? `${name}-${id}` : name;
  if ($(`#${panelId}`).length) {
    $(`#${panelId}`).css("zIndex", ++topZ);
    return;
  }
  const isFilteringPanel = panelId.includes("filtering");
  return jsPanel.create({
    id: panelId,
    border: "2px solid #2A3F52",
    theme: "light filledlight",
    headerLogo: "../static/images/logo.png",
    contentOverflow: "hidden scroll",
    contentSize: panelSize[name] || "1000 600",
    position: "center-top 0 10",
    headerTitle: title,
    contentAjax: {
      url: `../form/${name}`,
      done: function(panel) {
        panel.content.innerHTML = this.responseText;
        configureForm(name);
        preprocessForm(panel, id, type, duplicate);
        if (processing) processing(panel);
      },
    },
    dragit: {
      opacity: 0.6,
      containment: 0,
    },
    resizeit: {
      containment: 0,
    },
    onbeforeclose: function(panel, status) {
      if (isFilteringPanel) panel.minimize();
      return !isFilteringPanel;
    },
    setStatus: isFilteringPanel ? "minimized" : "normalized",
  });
}

/**
 * Generic Show Panel
 */
// eslint-disable-next-line
function showPanel(type, id, processing) {
  return createPanel(type, panelName[type] || type, id, processing);
}

/**
 * Show Filtering Panel
 */
// eslint-disable-next-line
function showFilteringPanel() {
  filteringPanel.normalize();
}

/**
 * Show Deletion Panel
 */
// eslint-disable-next-line
function showDeletionPanel(type, id, name) {
  createPanel("instance_deletion", `Delete ${name}`, id, () => {}, type);
}

/**
 * Preprocess form.
 * @param {JsPanel} panel - JsPanel element.
 * @param {int} id - Panel ID.
 * @param {string} type - Instance type.
 * @param {bool} duplicate - Duplicate instance.
 */
function preprocessForm(panel, id, type, duplicate) {
  panel.querySelectorAll(".add-id").forEach((el) => {
    if (duplicate && ["name", "id"].includes(el.name)) return;
    if (id) $(el).prop("id", `${$(el).attr("id")}-${id}`);
  });
  panel.querySelectorAll(".btn-id").forEach((el) => {
    if (id) {
      $(el).attr(
        "onclick",
        type ? `${el.value}("${type}", ${id})` : `${el.value}(${id})`
      );
    } else {
      $(el).attr("onclick", type ? `${el.value}("${type}")` : `${el.value}()`);
    }
  });
}

/**
 * Configure form.
 * @param {string} form - Form name.
 * @param {int} id - Form ID.
 */
function configureForm(form, id) {
  if (!formProperties[form]) return;
  for (const [property, type] of Object.entries(formProperties[form])) {
    let el = $(id ? `#${form}-${property}-${id}` : `#${form}-${property}`);
    if (!el.length) el = $(`#${property}`);
    if (type == "date") {
      el.datetimepicker({
        format: "DD/MM/YYYY HH:mm:ss",
        widgetPositioning: {
          horizontal: "left",
          vertical: "bottom",
        },
        useCurrent: false,
      });
    } else {
      el.selectpicker({
        liveSearch: true,
        actionsBox: true,
      });
    }
  }
}

/**
 * Display instance modal for editing.
 * @param {type} type - Type.
 * @param {id} id - Instance ID.
 * @param {duplicate} duplicate - Edit versus duplicate.
 */
// eslint-disable-next-line
function showTypePanel(type, id, duplicate) {
  createPanel(
    type,
    "",
    id,
    function(panel) {
      if (type == "workflow" || type.includes("Service")) panelCode(type, id);
      if (id) {
        call(`/get/${type}/${id}`, function(instance) {
          panel.setHeaderTitle(
            `${duplicate ? "Duplicate" : "Edit"} ${type} - ${instance.name}`
          );
          processInstance(type, instance);
          if (type == "workflow" && duplicate) {
            $(`#workflow-btn-${id}`).attr(
              "onclick",
              `duplicateWorkflow(${id})`
            );
          }
        });
      } else {
        panel.setHeaderTitle(`Create a New ${type}`);
      }
    },
    type,
    duplicate
  );
}

/**
 * Update property.
 * @param {jQuery} el - Property in the DOM.
 * @param {string} property - Property name.
 * @param {string} value - Property value.
 */
function updateProperty(el, property, value) {
  const propertyType = propertyTypes[property] || "str";
  if (propertyType.includes("bool") || property.includes("regex")) {
    el.prop("checked", value);
  } else if (propertyType.includes("dict")) {
    el.val(value ? JSON.stringify(value) : "{}");
  } else if (
    ["list", "multiselect", "object", "object-list"].includes(propertyType)
  ) {
    el.selectpicker("deselectAll");
    el.selectpicker(
      "val",
      propertyType === "object"
        ? value.id
        : propertyType === "object-list"
        ? value.map((p) => p.id)
        : value
    );
    el.selectpicker("render");
  } else {
    el.val(value);
  }
}

/**
 * Display instance modal for editing.
 * @param {type} type - Type.
 * @param {instance} instance - Object instance.
 */
function processInstance(type, instance) {
  for (const [property, value] of Object.entries(instance)) {
    const el = $(
      instance ? `#${type}-${property}-${instance.id}` : `#${type}-${property}`
    );
    updateProperty(el, property, value);
  }
}

/**
 * Create or edit instance.
 * @param {type} type - Type.
 */
// eslint-disable-next-line
function processData(type, id) {
  fCall(
    `/update/${type}`,
    id ? `#edit-${type}-form-${id}` : `#edit-${type}-form`,
    (instance) => {
      if (typeof table != "undefined") table.ajax.reload(null, false);
      $(id ? `#${type}-${id}` : `#${type}`).remove();
      if (type.includes("Service")) saveService(instance, id);
      if (type === "workflow" && !id) saveWorkflow(instance);
      alertify.notify(
        `${type.toUpperCase()} '${instance.name}' ${
          id ? "updated" : "created"
        }.`,
        "success",
        5
      );
    }
  );
}

/**
 * Create Table Search Headers.
 */
// eslint-disable-next-line
function createSearchHeaders() {
  properties.forEach((property) => {
    $(`#search-${property}`).on("keyup change", function() {
      $(`#${type}_filtering-${property}`).val($(this).val());
      table.ajax.reload(null, false);
    });
  });
}

/**
 * Datatable per-column search.
 * @param {cls} cls - Object class.
 * @param {type} type - Table type.
 * @return {table}
 */
// eslint-disable-next-line
function initTable(type) {
  const filteringPanel = showPanel(`${type}_filtering`);
  createSearchHeaders();
  // eslint-disable-next-line new-cap
  const table = $("#table").DataTable({
    serverSide: true,
    orderCellsTop: true,
    scrollX: true,
    sDom: "<'top'i>rt<'bottom'lp><'clear'>",
    ajax: {
      url: `/filtering/${type}`,
      type: "POST",
      data: (d) => {
        d.form = serializeForm(`#${type}_filtering-form`);
      },
    },
  });
  if (type == "log") {
    table.order([0, "desc"]).draw();
  }
  return [table, filteringPanel];
}

/**
 * Server-side table filtering.
 */
// eslint-disable-next-line
function filter(formType) {
  table.ajax.reload(null, false);
  alertify.notify("Filter applied.", "success", 5);
}

/**
 * Undo filter.
 */
// eslint-disable-next-line
function undoFilter(formType) {
  $(`#${formType}-form`)[0].reset();
  filteringPanel.minimize();
  table.ajax.reload(null, false);
  alertify.notify("Filter removed.", "success", 5);
}

/**
 * Datatable periodic refresh.
 * @param {interval} interval - Refresh interval.
 */
// eslint-disable-next-line
function refreshTable(interval) {
  table.ajax.reload(null, false);
  setTimeout(() => refreshTable(interval), 3000);
}

/**
 * Sidebar initialization.
 */
function initSidebar() {
  let setContentHeight = function() {
    $(".right_col").css("min-height", $(window).height());
    let bodyHeight = $("body").outerHeight();
    let footerHeight = $("body").hasClass("footer_fixed")
      ? -10
      : $("footer").height();
    let leftColHeight =
      $(".left_col")
        .eq(1)
        .height() + $(".sidebar-footer").height();
    let contentHeight = bodyHeight < leftColHeight ? leftColHeight : bodyHeight;
    contentHeight -= $(".nav_menu").height() + footerHeight;
    $(".right_col").css("min-height", contentHeight);
  };

  $("#sidebar-menu")
    .find("a")
    .on("click", function(ev) {
      let $li = $(this).parent();
      if ($li.is(".active")) {
        $li.removeClass("active active-sm");
        $("ul:first", $li).slideUp(function() {
          setContentHeight();
        });
      } else {
        if (!$li.parent().is(".child_menu")) {
          $("#sidebar-menu")
            .find("li")
            .removeClass("active active-sm");
          $("#sidebar-menu")
            .find("li ul")
            .slideUp();
        } else {
          if ($("body").is(".nav-sm")) {
            $("#sidebar-menu")
              .find("li")
              .removeClass("active active-sm");
            $("#sidebar-menu")
              .find("li ul")
              .slideUp();
          }
        }
        $li.addClass("active");
        $("ul:first", $li).slideDown(function() {
          setContentHeight();
        });
      }
    });

  $("#menu_toggle").on("click", function() {
    if ($("body").hasClass("nav-md")) {
      $("#sidebar-menu")
        .find("li.active ul")
        .hide();
      $("#sidebar-menu")
        .find("li.active")
        .addClass("active-sm");
      $("#sidebar-menu")
        .find("li.active")
        .removeClass("active");
    } else {
      $("#sidebar-menu")
        .find("li.active-sm ul")
        .show();
      $("#sidebar-menu")
        .find("li.active-sm")
        .addClass("active");
      $("#sidebar-menu")
        .find("li.active-sm")
        .removeClass("active-sm");
    }
    $("body").toggleClass("nav-md nav-sm");
    setContentHeight();
    $(".dataTable").each(function() {
      $(this)
        .dataTable()
        .fnDraw();
    });
  });

  // check active menu
  const url = "a[href='" + currentUrl + "']";
  $("#sidebar-menu")
    .find(url)
    .parent("li")
    .addClass("current-page");
  $("#sidebar-menu")
    .find("a")
    .filter(function() {
      return this.href == currentUrl;
    })
    .parent("li")
    .addClass("current-page")
    .parents("ul")
    .slideDown(function() {
      setContentHeight();
    })
    .parent()
    .addClass("active");

  setContentHeight();
  if ($.fn.mCustomScrollbar) {
    $(".menu_fixed").mCustomScrollbar({
      autoHideScrollbar: true,
      theme: "minimal",
      mouseWheel: { preventDefault: true },
    });
  }
}

(function($, window) {
  $.fn.contextMenu = function(settings) {
    return this.each(function() {
      $(this).on("contextmenu", function(e) {
        if (e.ctrlKey) {
          return;
        }
        const $menu = $(settings.menuSelector)
          .data("invokedOn", $(e.target))
          .show()
          .css({
            position: "absolute",
            left: getMenuPosition(e.clientX, "width", "scrollLeft"),
            top: getMenuPosition(e.clientY, "height", "scrollTop"),
          })
          .off("click")
          .on("click", "a", function(e) {
            $menu.hide();
            const $invokedOn = $menu.data("invokedOn");
            const $selectedMenu = $(e.target);
            settings.menuSelected.call(this, $invokedOn, $selectedMenu);
          });
        return false;
      });
      $("body").click(function() {
        $(settings.menuSelector).hide();
      });
    });

    /**
     * Get menu position.
     * @param {mouse} mouse
     * @param {direction} direction
     * @param {scrollDir} scrollDir
     * @return {position}
     */
    function getMenuPosition(mouse, direction, scrollDir) {
      const win = $(window)[direction]();
      const scroll = $(window)[scrollDir]();
      const menu = $(settings.menuSelector)[direction]();
      let position = mouse + scroll;
      // opening menu would pass the side of the page
      if (mouse + menu > win && menu < mouse) {
        position -= menu;
      }
      return position;
    }
  };
})(jQuery, window);

$(".dropdown-submenu a.menu-submenu").on("click", function(e) {
  $(this)
    .next("ul")
    .toggle();
  e.stopPropagation();
  e.preventDefault();
});

if (typeof NProgress != "undefined") {
  $(document).ready(function() {
    NProgress.start();
  });
  $(window).load(function() {
    NProgress.done();
  });
}

$(document).ready(function() {
  initSidebar();
  configureForm(page);
  doc(page);
});
