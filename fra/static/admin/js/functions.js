$(function() {


  let product_area = $('#product_area');
  let client = $('#client');

  product_area.empty();
  client.empty();

  product_area.append('<option selected="true" disabled>Select Product Area</option>');
  product_area.prop('selectedIndex', 0);

  client.append('<option selected="true" disabled>Select Client</option>');
  client.prop('selectedIndex', 0);

  // Populate dropdown with list of product area
  $.getJSON('/admin/get_product_area_options', function (data) {
    $.each(data, function (key, entry) {
      product_area.append($('<option></option>').attr('value', entry.id).text(entry.name));
    })
  });
  
  // Populate dropdown with list of clients
  $.getJSON('/admin/get_clients_options', function (data) {
    $.each(data, function (key, entry) {
      client.append($('<option></option>').attr('value', entry.id).text(entry.name));
    })
  });
           
});
