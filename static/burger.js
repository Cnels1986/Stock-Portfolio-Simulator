$(document).ready(function(){
  $("#burger").click(function(){
    $(this).toggleClass("open");
    $(".linkPanel").toggleClass("showPanel")
    window.setTimeout(function(){
      $("#link1").toggleClass('showLink');
    }, 100);
    window.setTimeout(function(){
      $("#link2").toggleClass('showLink');
    }, 250);
    window.setTimeout(function(){
      $("#link3").toggleClass('showLink');
    }, 400);
    window.setTimeout(function(){
      $("#link4").toggleClass('showLink');
    }, 550);
  })
  $("#walletButton").click(function(){
    $("#wallet").toggleClass('showWallet');
  })
  $("#wallet").click(function(){
    $("#wallet").toggleClass('showWallet');
  })
  $("#newsButton").click(function(){
    $(".stockNews").toggleClass('openNews');
  })

  // shows the introduction modal
  $("#introButton").click(function(){
    console.log("test");
    $("#introModalBackground").attr('style', 'display:block');
  })
  // hides the introduction modal
  $("#introModalButton").click(function(){
    $("#introModalBackground").attr('style', 'display:none');
  })
})
