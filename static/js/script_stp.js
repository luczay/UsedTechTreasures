$(document).ready(function(e) {

	$('#submit_btn').click(function(){
        scrape();
        return false;
    });

    $('#back_btn').click(function(){
        $('#content').remove();
        $('#time_est').remove();
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

/**
 * Performs web scraping based on user input and displays the results (if the user wants it).
 *
 * @function
 * @returns {boolean} Returns `false` if input validation fails, otherwise returns nothing.
 */
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

    // Validate the input values using the inputValidation() function and return false if validation fails
    valid_inputs = inputValidation(hardverapro, jofogas, marketplace, number_of_products, product_name, price_min, price_max);
    if (!valid_inputs) {
        return false;
    }

    $('#submit_btn_row').css('display', 'none');
    $('#loader').css('display', 'block');

    if ($('#display').is(':checked')) {
        var display = $('#display').val();
    } else {
        var display = '';
    }

    // Estimate the scraping time for each website based on the number of products to be scraped
    // est = load website/login/search/filter time + sleep times in an iteration * number of products
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
    $('#estimation').append('<p id="time_est">Estimated scraping time is ' + (scraping_time_est / 60).toFixed(1) + 'min</p>');

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

function inputValidation(hardverapro, jofogas, marketplace, number_of_products, product_name, price_min, price_max) {
    var valid = true;
    if ((hardverapro == '') && (jofogas == '') && (marketplace == '')) {
       alert('Pick at least one site to scrape!');
       valid = false;
    } else if (product_name == '') {
        alert('Scraping is not possible without a product name!')
        valid = false;
    } else if (price_min == '') {
        alert('Scraping is not possible without a minimum price!')
        valid = false;
    } else if (price_max == '') {
        alert('Scraping is not possible without a maximum price!')
        valid = false;
    } else if (number_of_products == '') {
        alert('Scraping is not possible without a quantity!')
        valid = false;
    }

    if (!valid) {
        return valid;
    }

    if (!$.isNumeric(price_min) || !$.isNumeric(price_max)) {
        alert('Price must be a number!')
        valid = false;
    } else if (!$.isNumeric(number_of_products)) {
        alert('Quantity must be a number!')
        valid = false;
    }

    if (!valid) {
        return valid;
    }

    price_min = parseInt(price_min)
    price_max = parseInt(price_max)
    number_of_products = parseInt(number_of_products)

    if (price_min < 0 || price_max < 0 || number_of_products < 0) {
        alert('Quantity, minimum price and maximum price must be a positive number!')
        valid = false;
    } else if (price_min >= price_max) {
        alert("The minimum price must be smaller than the maximum!")
        valid = false;
    }

    return valid;
};