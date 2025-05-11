/**
 * JavaScript for Survey Creation and Editing
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize flatpickr for date picker
    flatpickr("#end_date", {
        enableTime: false,
        dateFormat: "Y-m-d",
        minDate: "today"
    });

    // DOM Elements
    const questionsContainer = document.getElementById('questions-container');
    const addMultipleChoiceBtn = document.getElementById('add-multiple-choice');
    const addCheckboxBtn = document.getElementById('add-checkbox');
    const addTextBtn = document.getElementById('add-text');
    const questionsJsonInput = document.getElementById('questions_json');
    const submitButton = document.getElementById('submit-button');

    // Templates
    const multipleChoiceTemplate = document.getElementById('multiple-choice-template');
    const checkboxTemplate = document.getElementById('checkbox-template');
    const textTemplate = document.getElementById('text-template');
    const optionTemplate = document.getElementById('option-template');

    // Add Question Event Listeners
    if (addMultipleChoiceBtn) {
        addMultipleChoiceBtn.addEventListener('click', function() {
            addQuestion('multiple_choice');
        });
    }

    if (addCheckboxBtn) {
        addCheckboxBtn.addEventListener('click', function() {
            addQuestion('checkbox');
        });
    }

    if (addTextBtn) {
        addTextBtn.addEventListener('click', function() {
            addQuestion('text');
        });
    }

    // Functions
    function addQuestion(type) {
        let template;
        
        switch (type) {
            case 'multiple_choice':
                template = multipleChoiceTemplate.cloneNode(true);
                break;
            case 'checkbox':
                template = checkboxTemplate.cloneNode(true);
                break;
            case 'text':
                template = textTemplate.cloneNode(true);
                break;
            default:
                return;
        }
        
        // Generate a unique ID for the question
        const questionId = generateUniqueId();
        template.dataset.questionId = questionId;
        
        // Add event listener to remove question button
        template.querySelector('.remove-question').addEventListener('click', function() {
            template.remove();
            updateQuestionsJson();
            updateSubmitButtonState();
        });
        
        // For multiple choice and checkbox questions, add option buttons
        if (type === 'multiple_choice' || type === 'checkbox') {
            const addOptionBtn = template.querySelector('.add-option');
            const optionsContainer = template.querySelector('.options-container');
            
            // Add event listener to add option button
            addOptionBtn.addEventListener('click', function() {
                const option = optionTemplate.cloneNode(true);
                
                // Add event listener to remove option button
                option.querySelector('.remove-option').addEventListener('click', function() {
                    option.remove();
                    updateQuestionsJson();
                });
                
                optionsContainer.appendChild(option);
            });
            
            // Add two default options
            addOptionBtn.click();
            addOptionBtn.click();
        }
        
        // Add input event listeners to update the questions JSON
        const inputs = template.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('input', updateQuestionsJson);
        });
        
        // Add the question to the container
        questionsContainer.appendChild(template);
        
        // Update the questions JSON
        updateQuestionsJson();
        
        // Update submit button state
        updateSubmitButtonState();
    }

    function updateQuestionsJson() {
        const questions = [];
        
        // Get all question cards
        const questionCards = questionsContainer.querySelectorAll('.question-card');
        
        questionCards.forEach(card => {
            const questionId = card.dataset.questionId;
            const questionText = card.querySelector('.question-text').value.trim();
            
            // Determine question type
            let questionType;
            if (card.querySelector('.question-type i').classList.contains('fa-dot-circle')) {
                questionType = 'multiple_choice';
            } else if (card.querySelector('.question-type i').classList.contains('fa-check-square')) {
                questionType = 'checkbox';
            } else {
                questionType = 'text';
            }
            
            const question = {
                id: questionId,
                text: questionText,
                type: questionType
            };
            
            // For multiple choice and checkbox questions, get options
            if (questionType === 'multiple_choice' || questionType === 'checkbox') {
                const optionInputs = card.querySelectorAll('.option-text');
                const options = [];
                
                optionInputs.forEach(input => {
                    const optionText = input.value.trim();
                    if (optionText) {
                        options.push(optionText);
                    }
                });
                
                question.options = options;
            }
            
            questions.push(question);
        });
        
        // Update the hidden input
        questionsJsonInput.value = JSON.stringify(questions);
    }

    function updateSubmitButtonState() {
        if (questionsContainer.children.length > 0) {
            submitButton.removeAttribute('disabled');
        } else {
            submitButton.setAttribute('disabled', 'disabled');
        }
    }

    function generateUniqueId() {
        return 'q' + Math.random().toString(36).substr(2, 9);
    }

    // Handle form submission
    const surveyForm = document.getElementById('create-survey-form') || document.getElementById('edit-survey-form');
    
    if (surveyForm) {
        surveyForm.addEventListener('submit', function(e) {
            // Update questions JSON one last time
            updateQuestionsJson();
            
            // Get questions
            const questions = JSON.parse(questionsJsonInput.value);
            
            // Validate questions
            let isValid = true;
            
            if (questions.length === 0) {
                isValid = false;
                alert('Please add at least one question to your survey.');
            } else {
                questions.forEach(question => {
                    if (!question.text) {
                        isValid = false;
                        alert('Please provide text for all questions.');
                    }
                    
                    if ((question.type === 'multiple_choice' || question.type === 'checkbox') && 
                        (!question.options || question.options.length < 2)) {
                        isValid = false;
                        alert('Multiple choice and checkbox questions must have at least 2 options.');
                    }
                });
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    }
});