$(document).ready(function(e) {
	if (!($('#database').hasClass('active'))) {
		$('#database').addClass('active');
		$('#setup').removeClass('active');
	}

	$('#clear_btn').click(function(){
        clearDb();
        return false;
    });

	$('#submit_btn').click(function(){
		$('#success_display').css('display', 'none');
        search();
        return false;
    });

	search();
});

function clearDb() {
	$.post('/clear', {}, function() {
		$('#success_display').css('display', 'flex');
		$('.dataframe').remove();
	});
};

function search() {
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

	if ((hardverapro == '') && (jofogas == '') && (marketplace == '')) {
		alert('Pick at least one site to search!');
		return false;
	}

	var product_name = $('#product_name').val();
	var price_range = $('#price_range').val();

	$.post('/search', {product_name: product_name, price_range: price_range, jofogas: jofogas, marketplace: marketplace, hardverapro: hardverapro}, function(respond) {
		$('.dataframe').remove();
		$('#db_data_display').append(respond.table);
	});
};

