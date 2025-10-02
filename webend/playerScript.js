let lastSortedIndex = 0;
let sortAscending = true;
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
	
    const table = document.getElementById("listContainer");
	const header = table.querySelector(".header");
	header.querySelectorAll("span").forEach((span, index) => {
	  span.style.cursor = "pointer";
	  span.addEventListener("click", () => {
		const rows = Array.from(table.querySelectorAll("li:not(.header)"));

		// Determine sort order
		if (lastSortedIndex === index) {
		  // Flip order if same column clicked
		  sortAscending = !sortAscending;
		} else {
		  // New column clicked, start ascending
		  sortAscending = true;
		}
		lastSortedIndex = index;

		rows.sort((a, b) => {
		  let aText = a.children[index].textContent.trim();
		  let bText = b.children[index].textContent.trim();

		  // Numeric sorting if possible
		  const aNum = parseFloat(aText);
		  const bNum = parseFloat(bText);
		  if (!isNaN(aNum) && !isNaN(bNum)) {
			aText = aNum;
			bText = bNum;
		  }

		  if (aText < bText) return sortAscending ? -1 : 1;
		  if (aText > bText) return sortAscending ? 1 : -1;
		  return 0;
		});

		// Re-append rows in sorted order
		rows.forEach(row => table.appendChild(row));
		header.querySelectorAll("span").forEach((h, i) => {
			h.style.fontWeight = i === index ? "bold" : "normal";
		});
	  });

	});
});

// Function to get the value of a cookie
function getCookie(cookieName) {
	const cookies = document.cookie.split('; ');
	for (const cookie of cookies) {
		const [name, value] = cookie.split('=');
		if (name === cookieName) {
			return value;
		}
	}
	return null;
}

function setCookie(cookieName, value) {
	document.cookie = `${cookieName}=${value}`;
	
}

const initialDarkCookie=localStorage.getItem('darkmode')
if(initialDarkCookie=='sane'){
		activateLightMode();
		document.getElementById('saneMode').checked=true;
	}else if(initialDarkCookie=='dark'){
		activateDarkMode();
		document.getElementById('darkMode').checked=true;
	}else if(initialDarkCookie=='amoled'){
		activateAmoledMode();
		document.getElementById('amoledMode').checked=true;
	}
function activateLightMode(){
	const rootElement = document.documentElement;
	rootElement.removeAttribute('class');
	localStorage.setItem('darkmode','sane');
}

function activateDarkMode(){
	const rootElement = document.documentElement;
	rootElement.removeAttribute('class');
	rootElement.classList.add('darkmode');
	localStorage.setItem('darkmode','dark')
}

function activateAmoledMode(){
		const rootElement = document.documentElement;
	rootElement.removeAttribute('class');
	rootElement.classList.add('amoledmode');
	localStorage.setItem('darkmode','amoled')
}
