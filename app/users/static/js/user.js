// Preview selected image
const picInput = document.getElementById('picInput');
const profilePic = document.getElementById('profilePic');

if(profilePic){
    picInput.addEventListener('change', function(event) {
      const file = event.target.files[0];
      if (file) {
        profilePic.src = URL.createObjectURL(file);
      }
    });
}
