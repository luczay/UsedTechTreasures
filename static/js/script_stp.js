$(document).ready(function(e) {

	$('#submit_btn').click(function(){
        $('#submit_btn_row').css('display', 'none');
        $('#loader').css('display', 'block');
        scrape();
        return false;
    });

    $('#back_btn').click(function(){
        $('#content').remove();
        $('#scraped_data_div').css('display', 'none');
        $('#setup_display').css('display', 'block');
        $('#loader').css('display', 'none');
        $('#submit_btn_row').css('display', 'block');
        return false;
    });

    $('#save_btn').click(function(){
        save();
        return false;
    });
});

function scrape() {
    if ($('#hardverapro').is(':checked')) {
        var hardverapro = $('#hardverapro').val();
    } else {
        var hardverapro = '';
    }
    if ($('#jofogas').is(':checked')) {
        var jofogas = $('#jofogas').val();
    } else {
        var jofogas = '';
    }
    if ($('#marketplace').is(':checked')) {
        var marketplace = $('#marketplace').val();
    } else {
        var marketplace = '';
    }

    var number_of_products = $('#num_of_products').val();
    var product_name = $('#product_name').val();
    var price_min = $('#price_min').val();
    var price_max = $('#price_max').val();

    if ($('#display').is(':checked')) {
        var display = $('#display').val();
    } else {
        var display = '';
    }

    var m_scraping_time_est = 0
    var j_scraping_time_est = 0 
    var h_scraping_time_est = 0

    if (marketplace != '') {
        var m_scraping_time_est = 19 + (5 * number_of_products)
    }
    if (jofogas != '') {
        j_scraping_time_est = 3 + (2 * number_of_products)
    }
    if (hardverapro != '') {
        var h_scraping_time_est = 6 + (2 * number_of_products)
    }

    var scraping_time_est = m_scraping_time_est + j_scraping_time_est + h_scraping_time_est

    alert('Estimated scraping time is ' + (scraping_time_est / 60).toFixed(1) + 'min')

    var start_time = new Date()
    $.ajax({
        url: '/scrape',
        data: {hardverapro: hardverapro, jofogas: jofogas, marketplace: marketplace, 
                number_of_products: number_of_products, product_name: product_name,
                price_min: price_min, price_max: price_max, display: display},
        type: 'POST',
        dataType: 'json',
        timeout: 0,
        success: function(respond) { 
            var end_time = new Date()  
            var scraping_time = (end_time - start_time) / (1000 * 60) 
            alert('The scraping took ' + scraping_time.toFixed(1) + 'min')
            
            if (display == 'true') {
                $('#scraped_data_div').css('display', 'block');
                $('#setup_display').css('display', 'none');
                $('#scraped_data_display').append(respond.table);
            } else {
                $('.success_display').css('display', 'flexbox');
            }
    
            $('submit_btn_row').css('display', 'flex');
            $('loader').css('display', 'none');
        }
    });
};

function save() {
    $.post('/save', {}, function(respond) {
		if (respond.is_done == 'true') {
            alert('Saved')
            $('#save_btn').remove();
            } else {
            alert('Something went wrong')
        }
	});
};

function updateTextInput(val) {
    document.getElementById('textInput').value=val; 
  }