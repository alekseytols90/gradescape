$.bootstrapConfirm = function (title, message, callback) {
    $('#bootstrap-confirmation-title').html(title);
    $('#bootstrap-confirmation-body').html(message);
    $('#bootstrap-confirmation-modal').modal();
    $('#bootstrap-confirmation-no').off('click').click(function () {callback(0)});
    $('#bootstrap-confirmation-yes').off('click').click(function () {callback(1)});
}