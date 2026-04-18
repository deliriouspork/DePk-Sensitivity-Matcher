#include <unistd.h>
#include <grp.h>

int main() {
    gid_t gid = getegid();
    setgid(gid);
    setgroups(1, &gid);
    chdir("/usr/lib/depk-sensitivity-matcher");
    execl("/usr/bin/python", "python", "main.py", NULL);
    return 1;
}