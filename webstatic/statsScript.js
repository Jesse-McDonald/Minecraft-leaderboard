var total;
$(document).ready(function () {
	

	// Function to filter the list based on the search input.
	function filterList(searchValue) {
		const searchQuery = searchValue.toLowerCase();
		const listItems = document.querySelectorAll('.list-item');

		listItems.forEach(function(item, index) {
			const name = item.querySelector('.name').textContent.toLowerCase();
			
			// Always display the first item
			if (index === 0 || name.includes(searchQuery)) {
				item.style.display = 'flex';
			} else {
				item.style.display = 'none';
			}
		});
	}

	// Listen for changes in the search input.
	$('#searchInput').on('input', function () {
		filterList($(this).val());
	});

});
