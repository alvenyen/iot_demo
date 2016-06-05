$(document).ready(function() {

var node_table_refresh_timer = null;

function ajax_get(url, data, successCallback, isGlobal, errorCallback, isAsync) {
    if (isGlobal === undefined) {
        isGlobal = true;
    }
    if (isAsync == undefined) {
        isAsync = true;
    }
    var self = this;
    var deferred = $.Deferred();
    $.ajax({
        global: isGlobal,
        async: isAsync,
        cache: false,
        dataType: "json",
        data: data,
        url: url,
        beforeSend: function(jqXHR) {
        },
        success: function(data, statusText, jqXHR) {
            var ret = data.return_code;
            if (ret == 0) {
                if (successCallback) {
                    successCallback(data.response);
                }
                deferred.resolve(data, statusText, jqXHR);
            } else {
                if (errorCallback) {
                    errorCallback(data);
                } else {
                    alert(ret);
                }
                deferred.reject(data, statusText, jqXHR);
            }
        },
        error: function(jqXHR, statusText, errorThrown) {
            deferred.reject(jqXHR, statusText, errorThrown);
        },
        complete: function(jqXHR) {
        }
    });

    return deferred.promise();
}

function ajax_node_list(successCallback, isGlobal) {
    var data = {};
    return ajax_get("/cgi-bin/node_list.py", data, successCallback, isGlobal);
}

function ajax_node_control(node_id, component, command, successCallback, isGlobal) {
    var data = {
        node_id:node_id,
        component:component,
        command:command
    };
    return ajax_get("/cgi-bin/node_control.py", data, successCallback, isGlobal);
}

function ajax_node_add(node_id, node_name, successCallback, isGlobal) {
    var data = {
        node_id:node_id,
        node_name:node_name
    };
    return ajax_get("/cgi-bin/node_add.py", data, successCallback, isGlobal);
}

function ajax_node_delete(node_id_list, successCallback, isGlobal) {
    var data = {
        node_id_list:node_id_list.join(",")
    };
    return ajax_get("/cgi-bin/node_delete.py", data, successCallback, isGlobal);
}

function items_length(tableSelector) {
    var table = $(tableSelector).dataTable();
    return table.$("tr").length;
}

function iterate_items(tableSelector, callback) {
    var total = items_length(tableSelector);
    var table = $(tableSelector).dataTable();
    var count = 0;
    table.$("tr").each(function() {
        var row = this;
        var item = table.fnGetData(this);
        if ($(this).find("td:first-child input").prop("checked")) {
            if (callback) {
                if (++count == total) {
                    callback(true, true, item, row);
                } else {
                    callback(false, true, item, row);
                }
            }
        } else {
            if (callback) {
                if (++count == total) {
                    callback(true, false, item, row);
                } else {
                    callback(false, false, item, row);
                }
            }
        }
    });
}

function selected_item_length(tableSelector) {
    var count = 0;
    var table = $(tableSelector).dataTable();
    table.$("tr").each(function() {
        if ($(this).find("td:first-child input").prop("checked")) {
            count++;
        }
    });
    return count;
}

function iterate_selected_items(tableSelector, callback) {
    var count = 0;
    var total = selected_item_length(tableSelector);
    iterate_items(tableSelector, function(last, checked, item, row) {
        if (checked) {
            if (callback) {
                callback(++count==total, item, row);
            }
        }
    });
}

function update_node_button_status() {
    var num = selected_item_length("#node_table");
    if (num > 0) {
        $("#delete_node").attr("disabled", false);
    } else {
        $("#delete_node").attr("disabled", true);
    }
}

function init_exported_logs_table() {
    return $('#node_table').dataTable({
        "aoColumns": [
            {
                "bSortable": false,
                "sClass": "node-check center",
                "mData": null,
                "sWidth": "10%",
                "mRender": function(data, type, full) {
                    return '<input type="checkbox"></input>';
                }
            },
            {
                "sTitle": "Node Name",
                "sClass": "node-name center",
                "sWidth": "60%",
                "mData": "name"
            },
            {
                "sTitle": "Online",
                "sClass": "node-online center",
                "sWidth": "10%",
                "mData": function(source, type, val) {
                    if (type == 'set') {
                        source.online = val.online;
                        return;
                    } else if (type == undefined) {
                        if (source) {
                            return source;
                        } else {
                            return null;
                        }
                    } else {
                        if (source.online) {
                            return '<img src="images/GreenDot.png"></img>';
                        } else {
                            return '<img src="images/GrayDot.png"></img>';
                        }
                    }
                }
            },
            {
                "sTitle": "LED Control",
                "sClass": "led-control center",
                "sWidth": "10%",
                "mData": function(source, type, val) {
                    if (type == 'set') {
                        source.online = val.online;
                        source.led_state = val.led_state;
                        return;
                    } else if (type == undefined) {
                        if (source) {
                            return source;
                        } else {
                            return null;
                        }
                    } else {
                        var control_btn = $("<button>");
                        control_btn.attr("type", "button");
                        control_btn.addClass("btn btn-gray");
                        control_btn.css("width", "70px")
                        control_btn.text("LED On");
                        control_btn.addClass("led_on");
                        control_btn.attr("disabled", !source.online)

                        return control_btn[0].outerHTML;
                    }
                }
            }
        ],
        "fnDrawCallback": function(oSettings) {
            update_node_button_status();
            $(".node-check").click(update_node_button_status);
        },
        "fnRowCallback": function(nRow, aData, iDisplayIndex) {
            return nRow;
        },
        "bDestroy": true,
        "bStateSave": true
    });
}

$("#add_node").click(function(){
    $("#node_id_input").val("");
    $("#node_name_input").val("");
    $("#dialog_add_node").modal("show");
});

$("#dialog_add_node").on("shown.bs.modal", function(e){
    $("#add_node_submit").attr("disabled", false);
    $("#node_id_input").focus();
});

$("#add_node_submit").click(function(){
    var node_id = $("#node_id_input").val();
    var node_name = $("#node_name_input").val();
    $("#add_node_submit").attr("disabled", true);
    ajax_node_add(node_id, node_name, function(resp){
        $("#add_node_submit").attr("disabled", false);
        $("#dialog_add_node").modal("hide");
        refresh_node_table(false);
    });
});

$("#delete_node").click(function(){
    var node_id_list = [];
    if (selected_item_length("#node_table") > 0) {
        if (!confirm("Do you really want to delete these nodes?")) {
            return;
        }
    }
    iterate_selected_items("#node_table", function(last, node, row) {
        node_id_list.push(node.id);
        $("#node_table").dataTable().fnDeleteRow(row);
    });
    ajax_node_delete(node_id_list, function(){
        refresh_node_table(false);
    });
});

$("#delete_node").attr("disabled", true);

var node_table = init_exported_logs_table();

node_table.on("click", "button.led_on", function (e) {
    e.preventDefault();
    var parent = $(this).parents('tr');
    var data = node_table.fnGetData(parent);
    ajax_node_control(
        data["id"], 
        "led", 
        "on"
    );
} );

var refresh_node_table = function(recurrence) {
    ajax_node_list(function(resp){
        var num = selected_item_length("#node_table");
        if (num <= 0) {
            node_table.fnClearTable();
            var nodes = [];
            $.each(resp.nodes, function(node_id, node){
                item = {
                    "id": node.node_id,
                    "name": node.node_name,
                    "online": node.online
                };
                nodes.push(item);
            });
            node_table.fnAddData(nodes);
        }
    });
    if (recurrence) {
        node_table_refresh_timer = setTimeout(function() {
            refresh_node_table(true);
        }, 3000);
    }
}

refresh_node_table(true);

} );

//# sourceURL=node_config.js