console.log("script.js file loaded and executing.");

const logoImage = document.querySelector('.logo');
const API_BASE_URL = 'http://192.168.18.16:5000/api'; // IMPORTANT: Replace 192.168.1.12 with your PC's actual IPv4 address

function swapLogoOnResize() {
    if (!logoImage) return;

    const originalLogoSrc = logoImage.dataset.originalLogo;
    const alternateLogoSrc = logoImage.dataset.alternateLogo;

    if (window.innerWidth < 500) {
        logoImage.src = alternateLogoSrc;
        logoImage.classList.add('logo-alternate');
    } else {
        logoImage.src = originalLogoSrc;
        logoImage.classList.remove('logo-alternate');
    }
}

function onResize() {
    swapLogoOnResize();
}

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOMContentLoaded event fired. Attaching event listeners.");

    swapLogoOnResize();
    window.addEventListener('resize', swapLogoOnResize);
    const nameInput = document.getElementById('name-input');
    const searchButton = document.getElementById('searchStudentButton');
    const searchResult = document.getElementById('search-result');
    const semesterSelectContainer = document.querySelector('.api-semester-select');
    const studentSearchContainer = document.querySelector('.api-student-search');
    const semesterSelect = document.getElementById('semester-select');
    const classSelectContainer = document.querySelector('.api-class-select');
    const classSelect = document.getElementById('class-select');
    const showGradesContainer = document.querySelector('.api-show-grades');
    const midtermGradeEl = document.getElementById('midterm-grade');
    const finalGradeEl = document.getElementById('final-grade');
    const gradeRemarksEl = document.getElementById('grade-remarks');
    const backButton = document.getElementById('back-button');

    let currentStudentData = null;
    const getGradeClass = (grade) => {
        if (grade === null || grade === undefined) return '';
        if (grade < 60) return 'grade-fail';
        if (grade >= 60 && grade <= 75) return 'grade-passing';
        if (grade >= 76 && grade <= 85) return 'grade-good';
        if (grade >= 86 && grade <= 90) return 'grade-very-good';
        if (grade > 90) return 'grade-excellent';
        return '';
    };

    const setGrade = (element, grade) => {
        element.textContent = grade ?? 'N/A';
        element.className = '';
        element.classList.add(getGradeClass(grade));
    };

    const resetUI = () => {
        console.log("resetUI function called.");
        nameInput.value = '';
        searchResult.textContent = 'Test';
        searchResult.className = 'bricolage-font';
        searchResult.style.color = '';

        studentSearchContainer.style.display = 'flex';
        semesterSelectContainer.style.display = 'none';
        classSelectContainer.style.display = 'none';
        showGradesContainer.style.display = 'none';

        semesterSelect.innerHTML = '';
        classSelect.innerHTML = '';
    };

    const performSearch = async () => {
        console.log("performSearch function called.");
        searchResult.textContent = 'Searching...';
        searchResult.classList.remove('success', 'error');
        searchResult.style.color = 'white';
        studentSearchContainer.style.display = 'flex';
        semesterSelectContainer.style.display = 'none';
        semesterSelect.innerHTML = '';
        classSelectContainer.style.display = 'none';
        classSelect.innerHTML = '';
        showGradesContainer.style.display = 'none';

        const studentName = nameInput.value.trim();
        if (!studentName) {
            searchResult.textContent = 'Please enter a student name.';
            searchResult.classList.add('error');
            searchResult.classList.remove('success');
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/students/?name=${encodeURIComponent(studentName)}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ message: 'An unknown error occurred.' }));
                throw new Error(`HTTP error! status: ${response.status} - ${errorData.message}`);
            }

            const foundStudents = await response.json();

            if (foundStudents.length === 1) {
                const student = foundStudents[0];
                currentStudentData = student;
                searchResult.textContent = `Found: ${student.student_name}`;
                searchResult.classList.add('success');
                semesterSelectContainer.style.display = 'flex';
                semesterSelect.add(new Option('Select a semester...', ''));

                if (student.semesters.length > 0) {
                    student.semesters.forEach(semester => {
                        const option = new Option(semester.name, semester.id);
                        semesterSelect.add(option);
                    });
                } else {
                    semesterSelect.add(new Option('No semesters found for this student', ''));
                }
            } else if (foundStudents.length > 1) {
                searchResult.textContent = 'Multiple students found. Please be more specific.';
                searchResult.classList.add('error');
            } else {
                searchResult.textContent = 'Student not found';
                searchResult.classList.add('error');
            }

        } catch (error) {
            console.error('Error searching for student:', error);
            searchResult.textContent = 'Failed to connect to the API or an error occurred.';
            searchResult.classList.add('error');
        } finally {
            searchResult.style.color = '';
        }
    };

    searchButton.addEventListener('click', performSearch);

    nameInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault(); 
            performSearch();
        }
    });

    semesterSelect.addEventListener('change', () => {
        const selectedSemesterId = semesterSelect.value;
        if (selectedSemesterId) {
            studentSearchContainer.style.display = 'none';

            const selectedSemester = currentStudentData.semesters.find(s => s.id == selectedSemesterId);

            classSelect.innerHTML = '';
            classSelectContainer.style.display = 'flex';
            classSelect.add(new Option('Select a class...', ''));

            if (selectedSemester && selectedSemester.classes.length > 0) {
                selectedSemester.classes.forEach(cls => {
                    const option = new Option(cls.name, cls.id);
                    classSelect.add(option);
                });
            } else {
                classSelect.add(new Option('No classes found for this semester', ''));
            }
        } else {
            classSelectContainer.style.display = 'none';
            classSelect.innerHTML = '';
        }
    });

    classSelect.addEventListener('change', () => {
        const selectedClassId = classSelect.value;
        const selectedSemesterId = semesterSelect.value;

        if (selectedClassId) {
            semesterSelectContainer.style.display = 'none';

            const semester = currentStudentData.semesters.find(s => s.id == selectedSemesterId);
            const cls = semester.classes.find(c => c.id == selectedClassId);

            const grade = cls.grades[0]; 

            setGrade(midtermGradeEl, grade?.midterm_grade);
            setGrade(finalGradeEl, grade?.final_grade);
            gradeRemarksEl.textContent = grade ? (grade.description ?? 'No remarks.') : 'N/A';
            showGradesContainer.style.display = 'flex';

        } else {
            showGradesContainer.style.display = 'none';
        }
    });

    backButton.addEventListener('click', () => {
        resetUI();
    });
});
