
const imageBox = $('#image-preview');
const textBox = $('#text-preview');
const unsupportedBox = $('#preview-not-supported');
const fileName = $('#file-name');
const submitButton = $('#send');
const fileType = $('#file-type');
const fileUpload = document.getElementById('file-upload');

var is_url_required = false;

submitButton.click(function (event) {
    event.preventDefault();

    if (is_url_required) {
        if ($("#url-input").val().length <= 3) {
            alert("Please enter a valid URL to continue submission.");
            return;
        }
    }

    $.bootstrapConfirm("Submit this assignment?", "Are you sure you would like to submit this assignment? Once " +
    "submitted it cannot be changed.", function (status) {
        console.log("CALLED");
        if (status == 1) {
            console.log("submitting...");
            $('#upload-form').submit();
        }
    })

})

$('#send-link').click(function (event) {
    $("#upload-label").hide();
    $("#send-link").hide();
    $("#url-input").show();
    submitButton.removeClass('d-none');
    $("#url-input").focus();
    is_url_required = true;
});

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
        $("#send-link").hide();
    }
}

fileUpload.addEventListener('change', updateUpload);


