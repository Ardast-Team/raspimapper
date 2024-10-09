document.addEventListener('DOMContentLoaded', function() {
    // Function to create a new node
    window.createNode = function() {
        const nodeName = prompt("Enter the name of the new node:");
        if (nodeName) {
            // AJAX call to create a new node
            fetch('/grammar/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') // Ensure CSRF token is sent
                },
                body: JSON.stringify({ name: nodeName })
            })
            .then(response => response.json())
            .then(data => {
                // Update the tree structure in the UI
                // Logic to add the new node to the tree
            });
        }
    };

    // Function to import a file
    window.importFile = function() {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.onchange = e => {
            const file = e.target.files[0];
            const formData = new FormData();
            formData.append('file', file);

            fetch('/grammar/import/', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Logic to update the tree structure with parsed data
            });
        };
        fileInput.click();
    };

    // Function to export the grammar
    window.exportGrammar = function() {
        fetch('/grammar/export/', {
            method: 'GET'
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'grammar_file.txt'; // Change the filename as needed
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        });
    };

    // Function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Check if this cookie string begins with the name we want
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});