
document.addEventListener('DOMContentLoaded', () => {
  const fileInput      = document.getElementById('fileInput');
  const profilePicture = document.getElementById('profilePicture');
  const form           = document.getElementById('photoForm');
  
  if (!fileInput || !profilePicture || !form) return;
  profilePicture.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', () => {
    
    if (fileInput.files.length) form.submit();
  });
});
