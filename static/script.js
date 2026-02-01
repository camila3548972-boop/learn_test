document.addEventListener('DOMContentLoaded', function() {
    const postsContainer = document.getElementById('posts-container');

    // Ensure the Telegram Web App is ready
    window.Telegram.WebApp.ready();

    // Fetch posts from the API
    fetch('/api/posts')
        .then(response => response.json())
        .then(data => {
            // Clear the container first
            postsContainer.innerHTML = '';

            // Check if there are posts
            if (Object.keys(data).length === 0) {
                postsContainer.innerHTML = '<p>No posts found.</p>';
                return;
            }

            // Loop through each category and its posts
            for (const category in data) {
                const section = document.createElement('div');
                section.className = 'category-section';

                const title = document.createElement('h2');
                title.className = 'category-title';
                title.textContent = category;
                section.appendChild(title);

                data[category].forEach(post => {
                    const postElement = document.createElement('div');
                    postElement.className = 'post';

                    const postTitle = document.createElement('h3');
                    postTitle.className = 'post-title';
                    postTitle.textContent = post.title;
                    postElement.appendChild(postTitle);

                    const postText = document.createElement('p');
                    postText.className = 'post-text';
                    postText.textContent = post.text;
                    postElement.appendChild(postText);

                    section.appendChild(postElement);
                });

                postsContainer.appendChild(section);
            }
        })
        .catch(error => {
            console.error('Error fetching posts:', error);
            postsContainer.innerHTML = '<p>Error loading posts. Please try again later.</p>';
        });
});
