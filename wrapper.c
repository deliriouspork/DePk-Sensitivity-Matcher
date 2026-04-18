#include <unistd.h>

int main() {
    chdir("/usr/lib/depk-sensitivity-matcher");
    execl("/usr/bin/python", "python", "main.py", NULL);
    return 1;
}