#include "foo.h"
#include "bar.h"
#include "bar.h"


int main()
{
	TEST test_obj;

	foo( &test_obj );
	bar();

	printf( "function main\n" );
	printf( "print\n" );

	return 0;
}


