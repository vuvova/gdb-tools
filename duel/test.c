int foo = 1;
float bar = 2.0;
char *s = "s1";
long arr[] = {5, 10, 15, 20, 0};
struct {unsigned i; double r;} st = {123, 3.1415};
struct t { int v; struct t *left, *right; };
struct t t0={ 0,  0,  0}, t1={ 1,  0,  0}, t2={ 2,  0,  0}, t3={ 3,  0,  0},
         t4={ 4,  0,  0}, t5={ 5,  0,  0}, t6={ 6,  0,  0}, t7={ 7,  0,  0},
         t8={ 8,&t0,&t1}, t9={ 9,&t2,&t3}, ta={10,&t4,&t5}, tb={11,&t6,&t7},
         tc={12,&t8,&t9}, td={13,&ta,&tb}, te={14,&tc,&td}, *tree = &te;


int main()
{
  return 0;
}
