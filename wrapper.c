#include <unistd.h>
#include <grp.h>
#include <pwd.h>

int main() {
    // Get the input group GID
    struct group *input_grp = getgrnam("input");
    gid_t groups[] = { input_grp->gr_gid };

    // Drop to input group only, keep real user
    setgroups(1, groups);
    setgid(input_grp->gr_gid);

    // Drop root uid back to calling user
    setuid(getuid());

    chdir("/usr/lib/depk-sensitivity-matcher");
    execl("/usr/bin/python", "python", "main.py", NULL);
    return 1;
}