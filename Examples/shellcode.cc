
#include <dlfcn.h>

extern "C"
{
  struct args
  {
    const char name[256];
    decltype (&dlsym) dlsym;
  };
  void shellcode_entry (args *args)
  {
    auto dlopen_ = (decltype (&dlopen))args->dlsym (RTLD_DEFAULT, "dlopen");
    dlopen_ (args->name, RTLD_NOW);
 
  }
}