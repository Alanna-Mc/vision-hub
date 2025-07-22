// Ensures that only one checkbox can be checked at a time within each question block.
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.question-block').forEach(block => {
    const boxes = block.querySelectorAll('input[type="checkbox"]');
    boxes.forEach(box => {
      box.addEventListener('change', () => {
        if (box.checked) {
          boxes.forEach(other => {
            if (other !== box) other.checked = false;
          });
        }
      });
    });
  });
});
