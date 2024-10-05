$(document).ready(function() {
    // Function to truncate text
    function truncateText(text, length) {
        if (text.length <= length) {
            return text;
        } else {
            return text.substring(0, length) + '...'; // Append ellipsis
        }
    }

    var tableBody = $('#commentsTable');
    comments.forEach(function(comment, index) {
        var postText = truncateText(comment.post_text, 50); // Adjust length here
        var postComment = truncateText(comment.generated_comment, 50); // Adjust length here
        var row = `<tr>
            <th scope="row">${index + 1}</th>
            <td>
                <div class="text-preview">${postText}</div>
                <div class="text-more" style="display:none;">${comment.post_text}</div>
                <span class="show-more">more</span>
            </td>
            <td>
                <div class="text-preview">${postComment}</div>
                <div class="text-more" style="display:none;">${comment.generated_comment}</div>
                <span class="show-more">more</span>
            </td>
            <td>${comment.emotion}</td>
            <td>${new Date(comment.created_at).toLocaleString()}</td>
        </tr>`;
        tableBody.append(row);
    });

    // Show more/less functionality
    $('.show-more').on('click', function() {
        var $this = $(this);
        var $textMore = $this.siblings('.text-more');
        var $textPreview = $this.siblings('.text-preview');
        
        if ($textMore.is(':visible')) {
            $textMore.hide();
            $textPreview.show();
            $this.text('more');
        } else {
            $textMore.show();
            $textPreview.hide();
            $this.text('less');
        }
    });
});