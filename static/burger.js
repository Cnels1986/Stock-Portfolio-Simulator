$(document).ready(function(){
  $("#burger").click(function(){
    $(this).toggleClass("open");
    window.setTimeout(function(){
      $("#link1").toggleClass('showLink');
    }, 100);
    window.setTimeout(function(){
      $("#link2").toggleClass('showLink');
    }, 250);
    window.setTimeout(function(){
      $("#link3").toggleClass('showLink');
    }, 400);
  })
})
