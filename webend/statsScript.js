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
