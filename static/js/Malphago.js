var wins, ties, losses, my_choice;
var ready = true;
var blocked = false;
var choices = ['rock.png', 'paper.png', 'scissors.png'];

function get_result(choice){
	if (!ready) {
		setTimeout(get_result, 100, choice);
		if (!blocked){
			$.blockUI();
			blocked = true;
		}
		return
	} else if (blocked){
		$.unblockUI();
		blocked = false;
	}

	var result_div = document.getElementById('result');
	var user_img = document.getElementById('user');
	var my_img = document.getElementById('malphago');
	var output = document.getElementById('output');
	var stat_div = document.getElementById('stat');

	if (result_div.style.display == 'none'){
		result_div.style.display = 'block';
	}
	if (stat_div.style.display = 'none'){
		stat_div.style.display = 'block';
	}

	user_img.src = 'static/images/' + choices[choice];
	my_img.src = 'static/images/' + choices[my_choice];

	if (choice == my_choice) {
		output.innerHTML = 'We tied';
		ties++;
		document.getElementById('ties').innerHTML = ties;
	} else if ((choice - my_choice) % 3 == 1){
		output.innerHTML = 'You won';
		wins++;
		document.getElementById('wins').innerHTML = wins;
	} else {
		output.innerHTML = 'You lost';
		losses++;
		document.getElementById('losses').innerHTML = losses;
	}

	// get new my_choice according to curr state and update the state according to the user choice
	update_state(choice);
}

function update_state(choice) {
	ready = false;
	$.ajax({
		type: 'POST',
		url: 'http://localhost:5000/update_state',
		data: {'choice': choice},
		success: function(data){
			my_choice = data;	
			ready = true;
		},
		error: function(xhr, error){
			console.log(xhr);
			console.log(error);
		}
	});
}

function preload() {
	$.ajax({
		type: 'POST',
		url: 'http://localhost:5000/preload',
		dataType: 'json',
		success: function(data){
			var state = data['state'];
			wins = data['wins'];
			ties = data['ties'];
			losses = data['losses'];
			my_choice = data['my_choice'];

			if (state != 9) {

				last_choice = state % 3;
				my_last_choice = Math.floor(state / 3);

				var result_div = document.getElementById('result');
				var user_img = document.getElementById('user');
				var my_img = document.getElementById('malphago');
				var output = document.getElementById('output');
				var stat_div = document.getElementById('stat');

				result_div.style.display = 'block';
				stat_div.style.display = 'block';

				user_img.src = 'static/images/' + choices[last_choice];
				my_img.src = 'static/images/' + choices[my_last_choice];

				document.getElementById('ties').innerHTML = ties;
				document.getElementById('wins').innerHTML = wins;
				document.getElementById('losses').innerHTML = losses;
				if (last_choice == my_last_choice) {
					output.innerHTML = 'We tied';
				} else if (last_choice - my_last_choice == 1 || last_choice - my_last_choice == -2){
					output.innerHTML = 'You won';
				} else {
					output.innerHTML = 'You lost';
				}

			}
		},
		error: function(xhr, error){
			console.log(xhr);
			console.log(error);
		}
	});
}

preload();
