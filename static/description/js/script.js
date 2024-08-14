odoo.define('product_combo_pack.quote_configure', function (require) {
    "use strict";

    const $ = require('jquery');

    $(document).ready(function () {
        // Handle product selection
        $('#product_id').change(function () {
            const productId = $(this).val();
            if (productId) {
                $.ajax({
                    url: '/get/product_price',
                    type: 'POST',
                    contentType: 'application/json',
                    dataType: 'json',
                    data: JSON.stringify({product_id: productId}),
                    success: function (data) {
                        $('#price_unit').val(data.price);
                        calculateTotal();
                    },
                    error: function () {
                        $('#price_unit').val('Error');
                        $('#total').val('');
                    }
                });
            } else {
                $('#price_unit').val('');
                $('#total').val('');
            }
        });

        // Handle quantity change
        $('#quantity').on('input', function () {
            calculateTotal();
        });

        function calculateTotal() {
            const price = parseFloat($('#price_unit').val()) || 0;
            const quantity = parseFloat($('#quantity').val()) || 0;
            const total = price * quantity;
            $('#total').val(total.toFixed(2));
        }
    });
});
