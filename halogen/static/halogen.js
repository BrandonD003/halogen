
// Sets the selected options in a select field
function setSelected(optionList, optionId)
{
    $('.selectpicker').selectpicker('val', optionList);
    // for (var i = 0; i < optionList.length; i++)
    // {
    //     $('#benchmark_select option[value="' + optionList[i] + '"]').prop('selected', true);
    // }
    // $('.selectpicker').selectpicker('render');
}

function updateChart()
{
    // destroy the current chart. make a new one when the server responds
    $("#tabPanes .active").highcharts().destroy();

    // update the chart in the active tab
    $.getJSON($SCRIPT_ROOT + '/get_chart/', {
        statName:   selectedStatName,
        benchmarks: JSON.stringify($("#benchmark_select").val()),
        runs:       JSON.stringify($("#run_select").val()),
        normalize:  JSON.stringify($("#normalize").is(":checked")),
        average:    JSON.stringify($("#average").is(":checked")),
        hmean:      JSON.stringify($("#hmean").is(":checked"))
        },
        function(data) {
            // console.log("returned from getJSON: " + data.stat_long + " " + data.series[0].name + " " + data.series[0].data + " " + data.series[0].labels);
            
            $('#tabPanes .active').highcharts({
                title: {
                    text: data.stat_long
                },
                xAxis: {
                    categories: data.benchmarks
                },
                yAxis: {
                    title: {
                        text: data.stat
                }},
                series: data.series
            });

            // update the tab title
            $("#tabs .active a").text(data.stat);

            // create a list of benchmarks and run shown and select them in the select lists.
            var selectedOptions = data.benchmarks;
            $.each(data.series, function(i, series) {
                selectedOptions.push(series.name);
            });

            // unselect any "all" benchmarks and select each benchmark in the suite
            setSelected(selectedOptions, "#benchmark_select");
        }
    );
}

function addChart(tabName)
{
    // new tab will be active so deactivate current tab
    $( "#tabs .active" ).removeClass('active');
    $( "#tabPanes .active" ).removeClass('active');

    // create the tab and tab pane
    var newTab = "<li class=\"active\"><a href=\"#" + tabName + "\" data-toggle=\"tab\">" + tabName + "</a></li>"
    var newPane = jQuery('<div/>', {
        class: 'tab-pane active',
        id: tabName,
        style: 'min-height: 80%',
        text: 'chunky monkey'
        });
    // move the tab and pane to the front of their respective lists
    $( "#tabs" ).prepend(newTab);
    $( "#tabPanes" ).prepend(newPane);

    // create an empty chart in the tab pane
    $(newPane).highcharts({});

    // add the "Download CSV" option to the export menu
    Highcharts.getOptions().exporting.buttons.contextButton.menuItems.push({
        text: 'Download CSV',
        onclick: function () {
            // get
            $.get($SCRIPT_ROOT + '/get_csv/', {
                statName:   selectedStatName,
                benchmarks: JSON.stringify($("#benchmark_select").val()),
                runs:       JSON.stringify($("#run_select").val())
            }, function(csvContent) {
                // console.log("returned from get_csv: " + csvContent);
                var encodedUri = encodeURI(csvContent);
                var link = document.createElement("a");
                link.setAttribute("href", "data:text/csv;charset=utf-8," + encodedUri);
                link.setAttribute("download", selectedStatName + ".csv");
                link.click(); // This will download the data file named "<selectedStatName>.csv"
            });
        }
    });
}

var selectedStatName = "";
function setStat(statName) {
    selectedStatName = statName;

    $("#stat_title").text(statName);
    $("#stat_title").append(" <span class=\"caret\"></span>");
}
