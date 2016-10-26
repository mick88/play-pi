$(document).ready(function () {
    var currentStatus = "";

    // Search
    $('#search-box').keyup(function () {
        $('.thumbnail').each(function () {
            if ($(this).attr('name').toLowerCase().indexOf($('#search-box').val().toLowerCase()) == -1) {
                $(this).parent().hide();
            } else {
                $(this).parent().show();
            }
        });
    });

    // Add spacing and colour to thumbnail labels
    $(".thumbnail h3").wrapInner("<span>");
    $(".thumbnail h3 br").before("<span class='spacer'>").after("<span class='spacer'>");

    // Playback controls
    function ajax(toggle) {
        $.ajax("/ajax/" + toggle + "/", {type: "GET"}).always(function (response) {
            results = JSON.parse(response['responseText']);
            fetchCurrentlyPlaying();

            if (toggle === "random" || toggle === "repeat") {
                $("#" + toggle + "-button").parent().toggleClass('active');
            }
        });
        return false;
    }

    $('#random-button').click(function (e) {
        e.preventDefault();
        ajax("random");
    });

    $('#stop-button').click(function (e) {
        e.preventDefault();
        ajax("stop");
    });

    $('#repeat-button').click(function (e) {
        e.preventDefault();
        ajax("repeat");
    });

    $('#pause-button').click(function (e) {
        ajax("pause");
        $("#play-button").show();
        $("#pause-button").hide();
    });

    $('#play-button').click(function (e) {
        ajax("play");
        $("#play-button").hide();
        $("#pause-button").show();
    });

    $("#next-button").click(function (e) {
        ajax("next");
    });

    $("#previous-button").click(function (e) {
        ajax("previous");
    });

    $("#vol-up-button").click(function (e) {
        $.get('/ajax/volume_delta/5');
        // TODO: update volume slider to value from response
    });

    $("#vol-down-button").click(function (e) {
        $.get('/ajax/volume_delta/-5');
        // TODO: update volume slider to value from response
    });
    var currentTimeout = setTimeout(fetchCurrentlyPlaying, 5000);

    function fetchCurrentlyPlaying() {
        clearTimeout(currentTimeout);
        $.ajax("/ajax/current_song", {type: "GET"}).always(function (data) {
            currentTimeout = setTimeout(fetchCurrentlyPlaying, 5000);

            if (data == '{}') {
                $("#current-song").hide();
                $('#now-playing-popover').hide();
                return;
            }

            var data = JSON.parse(data['responseText']);
            $("#current-song-album").text(data.album);
            $("#current-song-title").text(data.title);
            $("#current-song-artist").text(data.artist);
            if (data.artist) {
                var title = data.artist + " - " + data.title;
            } else {
                var title = data.title;
            }
            $('#now-playing-popover').attr('data-content', title);
            currentStatus = data.state;
            if ((!data.album && !data.title && !data.artist) || currentStatus === "stop") {
                $("#current-song").hide();
                $('#now-playing-popover').hide();
            } else {
                $("#current-song").show();
                $('#now-playing-popover').show();
            }

            if (currentStatus === "play") {
                $("#play-button").hide();
                $("#pause-button").show();
            } else if (currentStatus === "pause") {
                $("#play-button").show();
                $("#pause-button").hide();
            } else if (currentStatus === "stop") {
                $("#play-button").show();
                $("#pause-button").hide();
            } else {
                $("#play-button").hide();
                $("#pause-button").hide();
            }
        });
    }

    $("#current-song").hide();
    fetchCurrentlyPlaying();
});

// Initialize volume slider
$('#volume-slider').slider({
    formatter: function (value) {
        return 'Volume: ' + value;
    }
});

$('#volume-slider').on('slideStop', function (event) {
    var volume = event.value;
    $.get('/ajax/volume/' + volume);
});

// Initialize "Now Playing" popup (mobile view)
$(function () {
    $('[data-toggle="popover"]').popover()
});