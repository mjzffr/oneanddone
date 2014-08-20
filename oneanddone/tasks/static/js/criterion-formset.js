/*
* This Source Code Form is subject to the terms of the Mozilla Public
* License, v. 2.0. If a copy of the MPL was not distributed with this
* file, You can obtain one at http://mozilla.org/MPL/2.0/.
*/
$(function () {
  var totalFormsField = $("#id_criterion-TOTAL_FORMS");

  $("#add_criterion").click(function () {
    var numForms = totalFormsField.val();
    if (parseInt(numForms) >= 10){
      $("#criterion_error_message").show();
      $("#criterion_error_message").fadeOut(3000);
      return;
    }
    var newForm = $("#empty_criterion_form").html().replace(/__prefix__/g, numForms);
    $("#criterion_formset_table tr:last").after(newForm);
    totalFormsField.val(parseInt(numForms) + 1);
    $("#del_criterion-" + numForms).click(delCriterion);
  });

  $("span[id|='del_criterion']").click(delCriterion);

  function delCriterion(event) {
    var currentRow = $("#" + event.target.id).parents("tr.extra-criterion");
    var rowsBelow = currentRow.nextAll();
    currentRow.remove();
    var numForms = parseInt(totalFormsField.val()) - 1;
    totalFormsField.val(numForms);
    var lastIndex = numForms - rowsBelow.length;
    rowsBelow.each(function (index, element) {
        var newIndex = lastIndex + index;
        updateIndexes($(this).find("[id]"), "id", newIndex);
        updateIndexes($(this).find("[name]"), "name", newIndex);
    });
  }

  function updateIndexes(elements, attribute, index) {
    elements.each(function () {
        var newValue = $(this).attr(attribute).replace(/criterion-\d+/, "criterion-"   + index);
        $(this).attr(attribute, newValue);
    });
  }
});
