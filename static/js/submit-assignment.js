
const imageBox = $('#image-preview');
const textBox = $('#text-preview');
const unsupportedBox = $('#preview-not-supported');
const fileName = $('#file-name');
const submitButton = $('#submit');
const fileType = $('#file-type');
const fileUpload = document.getElementById('file-upload');

$('#submit').click(function (event) {
    $.bootstrapConfirm("Submit this assignment?", "Are you sure you would like to submit this assignment? Once " +
    "submitted it cannot be changed.", function (status) {
        console.log("CALLED");
        if (status == 1) $('#upload-form').submit();
    })

})

function updatePreview (file) {
    resetPreview();
    switch (file.type.split('/')[0]) {
        case "image":
            displayImage(file);
            fileType.attr('value', 'image');
            break;
        case "text":
            displayText(file);
            fileType.attr('value', 'text');
            break;
        default:
            unsupportedBox.removeClass('d-none');
            fileType.attr('value', 'unsupported')
    }
}

function displayImage(file) {
    var reader = new FileReader();
    reader.onload = function (event) {
        imageBox.attr('src', event.target.result);
    }
    reader.readAsDataURL(file);
}

function displayText(file) {
    var reader = new FileReader();
    reader.onload = function (event) {
        textBox.html(event.target.result);
        textBox.removeClass('d-none');
        textBox.height(Math.min($('textarea#text-preview')[0].scrollHeight, 1000));
    }
    reader.readAsText(file);
}

function resetPreview() {
    imageBox.attr('src', null);
    textBox.html('');
    textBox.addClass('d-none');
    unsupportedBox.addClass('d-none');
}

window.addEventListener('paste', function (event) {
    if (event.clipboardData.files && event.clipboardData.files[0]) {
        fileUpload.files = event.clipboardData.files;
        updateUpload();
    }
 })

function updateUpload() {
    if (fileUpload.files && fileUpload.files[0]) {
        fileName.removeClass('d-none');
        fileName.html(fileUpload.files[0].name);
        submitButton.removeClass('d-none');
        updatePreview(fileUpload.files[0]);
        $('#preview-container').removeClass('d-none');
    }
}

fileUpload.addEventListener('change', updateUpload);