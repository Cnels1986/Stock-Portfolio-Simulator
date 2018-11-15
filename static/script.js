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

  var acc = document.getElementsByClassName("accordion");
  var i;

  for (i = 0; i < acc.length; i++) {
    acc[i].addEventListener("click", function() {
      this.classList.toggle("active");
      var panel = this.nextElementSibling;
      if (panel.style.maxHeight){
        panel.style.maxHeight = null;
      } else {
        panel.style.maxHeight = panel.scrollHeight + "px";
      }
    });
  }

  // gets the current and purchased prices of the stocks and changes the current price's color based on its value compared to purchased
  var currentPrice = document.getElementsByClassName("currentPrice");
  var purchasePrice = document.getElementsByClassName("purchasePrice");
  var percentChange = document.getElementsByClassName("percentChange");
  for(var a = 0; a < currentPrice.length; a++){
    // current price is less than the purchased price
    if( currentPrice[a].innerHTML < purchasePrice[a].innerHTML){
      var change = purchasePrice[a].innerHTML - currentPrice[a].innerHTML;
      var percent = (change/purchasePrice[a].innerHTML) * 100;
      console.log("Down: %" + percent.toFixed(2));
      percentChange[a].innerHTML = "- " + percent.toFixed(2) + "%";
      // percentChange[a].style.display = "block";
      percentChange[a].style.color = "red"
      currentPrice[a].style.color = "red";
    }
    // current price is more than the purchased price
    else if( currentPrice[a].innerHTML > purchasePrice[a].innerHTML){
      var change = currentPrice[a].innerHTML - purchasePrice[a].innerHTML;
      var percent = (change/purchasePrice[a].innerHTML) * 100;
      console.log("Up: %" + percent.toFixed(2));
      percentChange[a].innerHTML = "+ " + percent.toFixed(2) + "%";
      // percentChange[a].style.display = "block";
      percentChange[a].style.color = "green"
      currentPrice[a].style.color = "green";
    }
  }

});
