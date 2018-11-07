$(document).ready(function(){
  var path = window.location.pathname;
  var page = path.split("/").pop();

  var modal = document.getElementById('modalBackground');
  if(page == 'confirm')
  {
    var cancelPurchase = document.getElementById('cancelPurchase');
    var purchaseButton = document.getElementById('purchaseButton');
    purchaseButton.onclick = function() {
        var quantity = $("#stockQuantity").val();
        if (quantity != '' && quantity != '0'){
          var stock = $("#stock").text();
          var price = $("#price").text();
          var total = quantity * parseFloat(price);
          modal.style.display = "block";
          document.getElementById("modalQuantity").value = quantity;
          document.getElementById("modalQuantity").style.display = "none";
          document.getElementById("modalMessage").innerHTML = "Would you like to buy " + quantity + " stock(s) of " + stock + " for $" + total.toFixed(2);
        }
        else{
          var input = document.getElementById("stockQuantity");
          input.style.border = "2px solid red";
        }
    }
    cancelPurchase.onclick = function() {
        modal.style.display = "none";
    }
  }

  // if(page == 'sell')
  // {
  //   var cancelSell = document.getElementById('cancelSell');
  //   var sellButton = document.getElementsByClassName('sellButton');
  //   var stockPrices = document.getElementsByClassName('sellStockInput');
  //
  //   for(let i=0; i<sellButton.length; i++){
  //     sellButton[i].onclick = function(){
  //       var symbol = sellButton[i].value;
  //       var quantity = stockPrices[i].value;
  //       if(quantity != "" && quantity != '0'){
  //         modal.style.display = "block";
  //         document.getElementById("modalQuantity").value = quantity;
  //         document.getElementById("modalQuantity").style.display = "none";
  //         document.getElementById("modalMessage").innerHTML = "Would you like to sell " + quantity + " stock(s) of " + symbol;
  //       }
  //       else{
  //         var inputs = document.getElementsByClassName('sellStockInput');
  //         inputs[i].style.border = "2px solid red";
  //       }
  //     }
  //   }
  //   cancelSell.onclick = function() {
  //     modal.style.display = "none";
  //   }
  // }
});
