setTimeout(function() {
    var alert = document.querySelector('.alert');
        if (alert) {
            alert.style.display = 'none';
        }
}, 5000); // Hide alert after 5 seconds


document.addEventListener("DOMContentLoaded", function() {
    function toggleVisibility() {
        var content = document.getElementById('navbar');
        if (content.style.display === 'none') {
            content.style.display = 'block';  
        } else {
            content.style.display = 'none';  
        }
    }

});
