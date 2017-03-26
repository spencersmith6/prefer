$(document).ready(function(){

    function submitPreference(preferenceValue){
        $.ajax({
            method: 'POST',
            url: '/next_prefer',
            data: {
                product_id: $('#product-id').text(),
                preference: preferenceValue
            }
        }).done(function(newProduct){
            $('#product-id').text(newProduct.product_id)
            $('#product-name').text(newProduct.product_name)
            $('#product-img').attr("src", newProduct.product_image)
        }).fail(function(){
            console.log('failed') // debug statement
        })
    }

    function submitPreferenceClick(event){
        submitPreference($(event.target).text())
    }

    function submitPreferenceSwipe(event){
        if (event.type == 'swiperight'){
            submitPreference('Like')
        }
        else if (event.type == 'swipeleft'){
            submitPreference('Dislike')
        }
    }

    $('.preference-button').click(submitPreferenceClick)

    // prevent browser from dragging image during swipe
    $('#product-img').on('dragstart', function(event) {event.preventDefault()})
    $('#product-img').on('swipeleft', submitPreferenceSwipe)
    $('#product-img').on('swiperight', submitPreferenceSwipe)

})
