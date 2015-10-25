$(document).ready(function() {
    //Helper function to keep table row from collapsing when being sorted
    var fixHelperModified = function(e, tr) {
      var $originals = tr.children();  
      var $helper = tr.clone();
      $helper.children().each(function(index) {
        $(this).width($originals.eq(index).width())
      });
      return $helper;
    };

    //Make diagnosis table sortable
    $("#challenge_list tbody").sortable({
      helper: fixHelperModified,
      stop: function(event,ui) {
        renumber_table('#challenge_list');
        auto_update();
      }
    }).disableSelection();


    //Delete button in table rows
    $('table').on('click','.btn-delete',function() {
      tableID = '#' + $(this).closest('table').attr('id');
      r = confirm('Delete this item?');
      if(r) {
        $(this).closest('tr').remove();
        renumber_table(tableID);
        auto_update();
      }
    });
});

//Renumber table rows
function renumber_table(tableID) {
    $(tableID + " tr").each(function() {
      count = $(this).parent().children().index($(this)) + 1;
      $(this).find('.order').html(count);
    });
}

//Auto-update playlist ordering
function auto_update() {
  new_list = reorder_form();
  for (var i = 0; i < new_list.length; i++) {
    var elem = document.getElementById(new_list[i]);
    elem.value = i.toString();
  }
  var submit = document.getElementById('auto');
  submit.value = "Auto";
  document.getElementById("order-form").submit();
}

// Grab new table order
function reorder_form() {
  var sorted = [];
  $("#challenge_list tbody tr").each(function() {
    var name = $(this).find('.problem').text();
    sorted.push(name);
  });
  return sorted;
}