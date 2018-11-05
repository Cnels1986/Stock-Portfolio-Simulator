$(document).ready(function(){
  $("#purchaseButton").click(function(){
    var quantity = $("#stockQuantity").val();
    var stock = $("#stock").text();
    var price = $("#price").text();
    var total = quantity * parseFloat(price);
    confirm("Would you like to buy " + quantity + " stock(s) of " + stock + " for $" + total.toFixed(2));
  });

  $("#sellButton").click(function(){
    var quantity = $("#sellStock").val();
    var stock = $("#stock").text();
    confirm(stock);
  });
});
