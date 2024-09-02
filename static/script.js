// Handle video upload
document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const videoUrl = document.getElementById('videoUrl').value;

    fetch('/videos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: videoUrl })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Video uploaded successfully');
            location.reload();
        } else {
            alert('Failed to upload video');
        }
    });
});

// Handle liking video
function likeVideo(videoId) {
    fetch('/like', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ video_id: videoId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Liked!');
            location.reload();
        } else {
            alert('Failed to like video');
        }
    });
}

// Handle disliking video
function dislikeVideo(videoId) {
    fetch('/dislike', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ video_id: videoId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Disliked!');
            location.reload();
        } else {
            alert('Failed to dislike video');
        }
    });
}

// Handle following user
function followUser(userId) {
    fetch('/follow', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: userId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Followed!');
            location.reload();
        } else {
            alert('Failed to follow user');
        }
    });
}

// Handle unfollowing user
function unfollowUser(userId) {
    fetch('/unfollow', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: userId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Unfollowed!');
            location.reload();
        } else {
            alert('Failed to unfollow user');
        }
    });
}