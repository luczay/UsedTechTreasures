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

	$.post('/db_content', {}, function(respond) {
		$('#db_data_display').append(respond.table);
	});
});

function clearDb() {
	$.post('/clear', {}, function() {
		$('#success_display').css('display', 'flex');
		$('.dataframe').remove();
	});
};

function search() {
	var product_name = $('#product_name').val();
	var site = $('#site').val();
	var price_range = $('#price_range').val();

	$.post('/search', {product_name: product_name, site: site, price_range: price_range}, function(respond) {
		$('.dataframe').remove();
		$('#db_data_display').append(respond.table);
	});
};

