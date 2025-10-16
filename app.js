document.addEventListener('DOMContentLoaded', () => {
    const reviewContainer = document.getElementById('review-container');

    function fetchNextWord() {
        fetch('/api/next-word')
            .then(response => response.json())
            .then(word => {
                displayWord(word);
                if (word.word_id > 0) {
                    fetchAndDisplayExamples(word.word_id);
                }
            });
    }

    function displayWord(word) {
        reviewContainer.innerHTML = `
            <h2>${word.lemma}</h2>
            <p>${word.definition}</p>
            <div id="examples-container"></div>
            <button id="correct-btn">I knew it</button>
            <button id="incorrect-btn">I didn't know</button>
        `;

        if (word.word_id > 0) {
            document.getElementById('correct-btn').addEventListener('click', () => handleAnswer(word.word_id, true));
            document.getElementById('incorrect-btn').addEventListener('click', () => handleAnswer(word.word_id, false));
        }
    }

    function fetchAndDisplayExamples(wordId) {
        const examplesContainer = document.getElementById('examples-container');
        examplesContainer.innerHTML = '<p>Loading examples...</p>';

        fetch(`/api/examples/${wordId}`)
            .then(response => response.json())
            .then(examples => {
                if (examples.error) {
                    examplesContainer.innerHTML = `<p>${examples.error}</p>`;
                } else {
                    const examplesHtml = examples.map(example => `<p>${example}</p>`).join('');
                    examplesContainer.innerHTML = `
                        <h3>Example Sentences:</h3>
                        ${examplesHtml}
                    `;
                }
            });
    }

    function handleAnswer(wordId, isCorrect) {
        fetch('/api/update-status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                word_id: wordId,
                correct: isCorrect,
            }),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            fetchNextWord(); // Fetch the next word after answering
        });
    }

    fetchNextWord(); // Fetch the first word when the page loads
});