console.log("script.js loaded");

function submitMatchScores(matchForm) {
    matchForm.addEventListener('submit', function(event) {
        const matchTable = matchForm.querySelector('table.match-table');
        const tds = matchTable.querySelectorAll('td[type="set-score"]');
        let good_match = true;
        tds.forEach(td => {
            const input_j1 = td.querySelector('input[name^="set"][name$="_j1"]');
            const input_j2 = td.querySelector('input[name^="set"][name$="_j2"]');
            const score_j1 = parseInt(input_j1.value, 10);
            const score_j2 = parseInt(input_j2.value, 10);

            let good_score = false;
            if (score_j1 >= 0 || score_j2 >= 0) {
                if ((score_j1 >= 10 && score_j2 >= 10) && (Math.abs(score_j1 - score_j2) === 2)) {
                    good_score = true;
                } else if ((score_j1 === 11 && score_j2 <= 9) || (score_j2 === 11 && score_j1 <= 9)) {
                    good_score = true;
                }
            } else if (isNaN(score_j1) && isNaN(score_j2) && input_j1.required === false && input_j2.required === false) {
                good_score = true; // Both fields are empty, meaning the set was not played
            }
            console.log(`Scores: J1=${score_j1}, J2=${score_j2}, valid=${good_score}`);
            
            if (!good_score) {
                good_match = false;
            }
        });
        if (!good_match) {
            event.preventDefault();
            alert("Veuillez entrer des scores valides pour tous les sets.");
            return;
        }
        // If all scores are valid, the form will be submitted automatically (default behavior
        // of the submit event unless prevented 
        // by calling event.preventDefault()
        // as done above in case of invalid scores
        console.log("All scores are valid, submitting the form.")
    });
}

const matchForm = document.querySelector('form.match-form');
if (matchForm !== null) {
    console.log("Match form found, setting up submission handler.");
    submitMatchScores(matchForm);
}