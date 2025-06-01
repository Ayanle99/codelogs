let user_info = document.querySelector('.user-info-restults');
let form = document.getElementById('searchForm');
let status = document.getElementById('search-status');

if (form) {
    form.addEventListener('submit', function (e) {
        e.preventDefault();  // Prevent actual submission

        let username = form.username.value.trim();

        if (!username) {
            console.log('Username is empty.');
            return;
        }

        fetch(`/users/search?username=${encodeURIComponent(username)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`User not found: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                if (user_info) {
                    const followersUrl = `/users/followers/${encodeURIComponent(data.username)}`;
                    const followingUrl = `/users/following/${encodeURIComponent(data.username)}`;

                    user_info.innerHTML = `

                        <div tabindex="-1" id="search-result-focus" class="card shadow-sm mx-auto text-center" style="max-width: 400px;">
                            <div class="card-body p-4">
                                <h2 class="card-title h4 fw-bold text-dark mb-3">${data.username}</h2>
                                <img src="${data.thumbnail_url}"
                                     alt="Profile picture of ${data.username}"
                                     aria-label="Profile picture of ${data.username}"
                                     class="rounded-circle border border-3 border-light shadow-sm mb-3"
                                     width="100"
                                     height="100"
                                     style="object-fit: cover;">
                                <div class="text-center">
                                    ${
                                      data.current_user === data.username
                                        ? `<p class="mb-2 text-muted" aria-label="${data.username}'s email address is ${data.email}">
                                              <strong class="text-secondary">Email &#128232;</strong> ${data.email}
                                           </p>`
                                        : ''
                                    }
                                    <p class="mb-2 text-muted" aria-label='${data.username} joined ${data.joined_on}'>
                                        <strong class="text-secondary">Joined &#128197;</strong> ${data.joined_on}
                                    </p>
                                    <p class="mb-3 text-muted">
                                        <strong class="text-secondary fst-italic">Bio</strong> ${data.bio || 'No bio available.'}
                                    </p>

                                <a href="${data.profile_url}" class="btn btn-outline-info w-100 rounded-pill fw-semibold">
                                    View Profile
                                </a>
                            </div>
                        </div>

                        <div class="stats d-flex justify-content-center gap-5 my-4 p-4 bg-secondary bg-opacity-25 rounded-3 w-100" role="list" aria-label="User statistics">
                              <div class="text-center" role="listitem">
                                <strong class="d-block display-5 text-primary">${data.posts_count}</strong>
                                <p class="mb-0 text-muted fs-5">posts</p>
                              </div>
                              <div class="text-center" role="listitem">
                                <strong class="d-block display-5 text-primary">
                                  <a href="${followingUrl}" class="text-decoration-none link-primary">
                                    ${data.following_count}
                                  </a>
                                </strong>
                                <p class="mb-0 text-muted fs-5">following</p>
                              </div>
                              <div class="text-center" role="listitem">
                                <strong class="d-block display-5 text-primary">
                                  <a href="${followersUrl}" class="text-decoration-none link-primary">
                                    ${data.followers_count}
                                  </a>
                                </strong>
                                <p class="mb-0 text-muted fs-5">followers</p>
                              </div>
                        </div>
                    `;

                    if (status) {
                        status.textContent = `User ${data.username} found. Profile information displayed.`;
                    }

                    let resultFocus = document.getElementById('search-result-focus');
                    if (resultFocus) {
                        resultFocus.focus();
                    }
                }
            })
            .catch(error => {
                console.error(error);
                if (user_info) {
                    user_info.innerHTML = `<p class="text-danger" tabindex="-1" id="search-result-focus">User not found or error occurred.</p>`;
                    let resultFocus = document.getElementById('search-result-focus');
                    if (resultFocus) {
                        resultFocus.focus();
                    }
                }

                if (status) {
                    status.textContent = `User not found. Please try again.`;
                }
            });
    });
}
