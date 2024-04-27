#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>

/*
I obtained access to the professor's grade management program.
Can I change my grade to an 'A' and also get access to the shell?
*/

typedef struct Student_
{
    char name[40];
    char passcode[4];
    int student_number;
    char grade[4];
} Student;

void menu(Student *student);
void input(Student *student);
void print_info(Student *student);
void graduate_school_application(Student *student);
void init_passcode(Student *student);

void menu(Student *student)
{
    int num;
    printf("1: Input\n2: Print info\n3: graduate_school_application\n");
    scanf("%d", &num);
    if (num == 1)
        input(student);
    else if (num == 2)
        print_info(student);
    else if (num == 3)
        graduate_school_application(student);
    else
        printf("num error\n");
    return;
}

void input(Student *student)
{
    char passcode[4];
    printf("enter below informations.\n\n");
    printf("[student number]\n");
    scanf("%d", &student->student_number);
    printf("[name]\n");
    read(0, student->name, 40);
    printf("[grade]\n");
    read(0, student->grade, 5);
    if (strncmp(student->grade, "A+", 2) == 0)
    {
        printf("To award an A+ grade, please enter the passcode:\n");
        read(0, passcode, 4);
        if (strncmp(student->passcode, passcode, 4) != 0)
        {
            printf("Error. You will get F grade.\n");
            strcpy(student->grade, "F");
        }
    }
}

void print_info(Student *student)
{
    printf("name : %s\n", student->name);
    printf("student number : %d\n", student->student_number);
}

void graduate_school_application(Student *student)
{
    if (strncmp(student->grade, "A+", 2))
    {
        printf("You need to have an A+ grade to apply to the graduate school\n");
        return;
    }
    printf("Congratulation! you can apply graduate school ^^\n");
    printf("Please enter your name\n");
    read(0, student->name, 100);
    printf("Well done. I'll text you soon.\n");
    printf("And... this is present for you.\n");
    printf("%p\n", &student->name);
    return;
}

void init_passcode(Student *student)
{
    int i;
    for (i = 0; i < 4; i++)
    {
        student->passcode[i] = rand() % 256;
    }
}

int main()
{
    int i;
    Student student = {"", "", 0, ""};

    setvbuf(stdin, 0, _IONBF, 0);  // Function for setting up remote. You don't need to care about it when solving the problem.
    setvbuf(stdout, 0, _IONBF, 0); // Function for setting up remote. You don't need to care about it when solving the problem.

    srand((unsigned int)time(NULL));

    printf("[Professor's grade management program]\n\n");

    init_passcode(&student);
    for (i = 0; i < 10; i++)
    {
        menu(&student);
    }
    return 0;
}
