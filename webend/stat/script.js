var total;
$(document).ready(function () {
	const params = new URLSearchParams(window.location.search);
	const statParam = params.get('stat');
	const statName=params.get('stat');
	const jsonUrl = statName+'.json'; // The path to your JSON file.
	$('h1').append(statName)
	$('title').append(": "+statName)
	function calculateTotal(data) {
		let total = 0;
			data.forEach(item => {
			total += item.amount;
		});
		if (total===0){
			total=1;
		}
		return total;
	}
	// Function to populate the list from JSON data.
	function populateList(data) {
		const listContainer = $('#listContainer');
		listContainer.empty();

		// Sort the data based on the 'number' field (largest to smallest).
		data.sort((a, b) => b.number - a.number);

		// Iterate through the sorted data and create list items.
		
		data.forEach((item, index) => {
			const listItem = $('<li>', { class: 'list-item' });
			listItem.append(`<span class='rank'>${index + 1}:</span>`); 
			listItem.append(`<span class='name'>${item.name}</span>`);
			listItem.append(`<span class='number'>${item.amount}</span>`);
			listItem.append(`<span class='percentage'>${Math.round(item.amount*100/total)}%</span>`);
		
			// Create a colored background "bar" based on the percentage of total.
			const progressBar = $('<div>', { class: 'progress-bar' });
			const progressBarFill = $('<div>', { class: 'progress-bar-fill' });
			const percentage = (item.amount / total) * 100;
			progressBarFill.css('width', `${percentage}%`);
			progressBar.append(progressBarFill);
			listItem.append(progressBar);
			//listItem.append(progressBarFill);
			listContainer.append(listItem);
			
		});
		
	}

	// Function to filter the list based on the search input.
	function filterList(searchValue) {
		const data = jsonData.filter(item => item.name.	toLowerCase().includes(searchValue.toLowerCase()));
		populateList(data);
	}

	// Fetch JSON data from the server and populate the list.
	$.getJSON(jsonUrl, function (data) {
		// Store the original data to reset the list on search.
		window.jsonData = data;
		total = calculateTotal(data);
		const totalElement = $('<div>', { class: 'total' });
		totalElement.text(`Total: ${total}`);
		$('#listContainer').after(totalElement);
		populateList(data);
	});

	// Listen for changes in the search input.
	$('#searchInput').on('input', function () {
		filterList($(this).val());
	});

});