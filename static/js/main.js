document.addEventListener("DOMContentLoaded", function() {
  // Select all list items in the navigation
  let listItems = document.querySelectorAll(".navigation ul li");

  // Function to handle the active state when a tab is clicked
  function setActiveTab() {
    // Remove the 'hovered' class from all items
    listItems.forEach((item) => {
      item.classList.remove("hovered");
    });

    // Add the 'hovered' class to the clicked item
    this.classList.add("hovered");

    // Store the index of the clicked tab in local storage
    let index = Array.from(listItems).indexOf(this);
    localStorage.setItem('activeTabIndex', index);
  }

  // Add click event listener to each item to handle activation
  listItems.forEach((item) => {
    item.addEventListener("click", setActiveTab);
  });

  // Mark the saved tab as active initially (if available)
  let savedIndex = localStorage.getItem('activeTabIndex');
  if (savedIndex !== null) {
    listItems[savedIndex].classList.add('hovered');
  } else if (listItems.length > 0) {
    // If no tab is saved, mark the first tab as active by default
    listItems[1].classList.add('hovered');
  }
});
