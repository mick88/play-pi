$(document).ready(function() {
  var currentStatus = "";
  $('#search-box').keyup(function() {
    $('.thumbnail').each(function(){
        if($(this).attr('name').toLowerCase().indexOf($('#search-box').val().toLowerCase()) == -1){
            $(this).parent().hide();
        }else{
            $(this).parent().show();
        }
    });
  });
  
  $(".thumbnail h3").wrapInner("<span>");
  $(".thumbnail h3 br").before("<span class='spacer'>").after("<span class='spacer'>");

  function ajax(toggle){
    $.ajax("/ajax/"+toggle+"/",{ type: "GET" }).always(function (response) {
      results = JSON.parse(response['responseText']);
      fetchCurrentlyPlaying();
      
      if(toggle === "random" || toggle === "repeat"){
        $("#"+toggle+"-button").toggleClass('btn-highlight');
      }
    });
    return false;
  }

  $('#random-button').click(function(e){
      e.preventDefault();
      ajax("random");
  });
  $('#stop-button').click(function(e){
      e.preventDefault();
      ajax("stop");
  });
  $('#repeat-button').click(function(e){
      e.preventDefault();
      ajax("repeat");
  });
  $('#pause-button').click(function(e) {
    ajax("pause");
    $("#play-button").show();
    $("#pause-button").hide();
  });
  $('#play-button').click(function(e) {
    ajax("play");
    $("#play-button").hide();
    $("#pause-button").show();
  });
  $("#next-button").click(function(e) {
    ajax("next");
  });
  $("#previous-button").click(function(e) {
    ajax("previous");
  });
  var currentTimeout = setTimeout(fetchCurrentlyPlaying, 5000);
  function fetchCurrentlyPlaying() {
    clearTimeout(currentTimeout);
    $.ajax("/ajax/current_song",{type: "GET"}).always(function(data) {
      currentTimeout = setTimeout(fetchCurrentlyPlaying, 5000);
      
      var data = JSON.parse(data['responseText']);
      $("#current-song-album").text(data.album);
      $("#current-song-title").text(data.title);
      $("#current-song-artist").text(data.artist);
      currentStatus = data.state;
      if((!data.album && !data.title && !data.artist) || currentStatus === "stop") {
        $("#current-song").hide();
      } else {
        $("#current-song").show();
      }
      
      if(currentStatus === "play") {
        $("#play-button").hide();
        $("#pause-button").show();
      } else if (currentStatus === "pause") {
        $("#play-button").show();
        $("#pause-button").hide();
      } else {
        $("#play-button").hide();
        $("#pause-button").hide();
      }
    });
  }
  $("#current-song").hide();
  $("#play-button").hide();
  fetchCurrentlyPlaying();
});

$('#volume-slider').slider({
	formatter: function(value) {
		return 'Volume: ' + value;
	}
});
$('#volume-slider').on('slideStop', function (event) {
    var volume = event.value;
    $.get('/ajax/volume/' + volume);
});