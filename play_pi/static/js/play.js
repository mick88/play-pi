// API URL definitions
const API_BASE = '/api/';
const API_STATUS = API_BASE + 'status/';
const API_JUMP = API_BASE + 'jump/';
const API_QUEUE = API_BASE + 'queue/';
const API_NOW_PLAYING = API_BASE + 'queue/current';

var lastStatus = {};
var nowPlaying = {}


function onStatusChange(status) {
    lastStatus = status;
    updateUi(status);
}

function updateUi(status) {
    // using switch because we're only interested in true/false state.
    // random/repeat etc could also be undefined
    switch (status.random) {
        case true:
            $("#random-button").parent().addClass('active');
            break;
        case false:
            $("#random-button").parent().removeClass('active');
            break;
    }

    switch (status.repeat) {
        case true:
            $("#repeat-button").parent().addClass('active');
            break;
        case false:
            $("#repeat-button").parent().removeClass('active');
            break;
    }

    switch (status.state) {
        case 'play':
            $("#play-button").hide();
            $("#pause-button").show();
            break;
        case 'pause':
        case 'stop':
            $("#play-button").show();
            $("#pause-button").hide();
            break;
    }

}

/**
 * Sends status update to the API
 * @param status - the status dict
 */
function sendStatus(status) {
    updateUi(status);
    $.post(API_STATUS, status, function (data, status) {
        onStatusChange(data);
    });
}

function fetchStatus() {
    $.get(API_STATUS, function (data, status) {
        onStatusChange(data);
    });
}

/**
 * Jump to item in queue
 * @param to String: track|radio|next|previous
 * @param item track or radio object. Not required for next/previous
 */
function jump(to, item) {
    $.post(API_JUMP + to, status, function (item, status) {
        // TODO: Refresh current song
    });
}

$(document).ready(function () {
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

    $('#random-button').click(function (e) {
        var random = lastStatus == null ? false : lastStatus['random'];
        sendStatus({
            'random': !random
        });
    });

    $('#stop-button').click(function (e) {
        sendStatus({
            'state': 'stop'
        });
    });

    $('#repeat-button').click(function (e) {
        var repeat = lastStatus == null ? false : lastStatus['repeat'];
        sendStatus({
            'repeat': !repeat
        });
    });

    $('#pause-button').click(function (e) {
        sendStatus({
            'state': 'pause'
        });

    });

    $('#play-button').click(function (e) {
        sendStatus({
            'state': 'play'
        });
    });

    $("#next-button").click(function (e) {
        jump('next');
    });

    $("#previous-button").click(function (e) {
        jump('previous');
    });

    $("#vol-up-button").click(function (e) {
        sendStatus({
            'volume': '+5'
        });
    });

    $("#vol-down-button").click(function (e) {
        sendStatus({
            'volume': '-5'
        });
    });
    var currentTimeout = setTimeout(fetchCurrentlyPlaying, 5000);

    function fetchCurrentlyPlaying() {
        clearTimeout(currentTimeout);
        fetchStatus();

        $.get(API_NOW_PLAYING, function (data, status) {
            currentTimeout = setTimeout(fetchCurrentlyPlaying, 5000);
            nowPlaying = data;

            var show = lastStatus.state != 'stop';

            if (data.track) {
                var track = data.track;
                $("#current-song-title").text(track.name);
                $("#current-song-artist").text(track.artist.name);
                $('#now-playing-popover').attr('data-content', track.artist.name + " - " + track.name);
            } else if (data.radio_station) {
                var radio = data.radio_station;
                $("#current-song-title").text(radio.name);
                $("#current-song-artist").text('Radio');
                $('#now-playing-popover').attr('data-content', radio.name);
            } else {
                show = false;
            }

            if (show) {
                $("#current-song").show();
                $('#now-playing-popover').show();
            } else {
                $("#current-song").hide();
                $('#now-playing-popover').hide();
            }
        });

    }

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
    sendStatus({
        'volume': volume
    });
});

// Initialize "Now Playing" popup (mobile view)
$(function () {
    $('[data-toggle="popover"]').popover()
});