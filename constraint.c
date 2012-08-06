/* ---------------------------------------------------------------------- */
/* Stage 1: determine the straight subpaths (Sec. 2.2.1). Fill in the
   "furthest_straight_vertex" component of a path objedir_list (based on path/len).	For each i,
   furthest_straight_vertex[i] is the furthest index such that a straight line can be drawn
   from i to furthest_straight_vertex[i]. Return 1 on error with errno set, else 0. */

/* this algorithm depends on the fadir_list that the existence of straight
   subpaths is a triplewise property. I.e., there exists a straight
   line through squares i0,...,in iff there exists a straight line
   through i,j,k, for all i0<=i<j<k<=in. (Proof?) */

/* this implementation of calc_furthest_straight_vertex is O(path_length^2). It replaces an older
   O(path_length^3) version. A "constraint" means that future points must
   satisfy xprod(constraint[0], cur) >= 0 and xprod(constraint[1],
   cur) <= 0. */

static int calc_furthest_straight_vertex(path_t *p) {
  point_t *path = p->path;
  int path_length = p->len;
  int i, j, k;
  int pivk[path_length];
  int dir_list[4], dir;
  point_t constraint[2];
  point_t cur;
  point_t off;

  p->furthest_straight_vertex = malloc(path_length*sizeof(int));
  if (!p->furthest_straight_vertex) {
    return 1;
  }

  /* determine pivot points: for each i, let pivk[i] be the furthest k
     such that all j with i<j<k lie on a line connecting i,k. */
  
  for (i=path_length-1; i>=0; i--) {
    dir_list[0] = dir_list[1] = dir_list[2] = dir_list[3] = 0;

    /* keep track of "directions" that have occurred */
    dir = (3+3*(path[mod(i+1,path_length)].x-path[i].x)+
            (path[mod(i+1,path_length)].y-path[i].y))/2;
    dir_list[dir]++;

    constraint[0].x = 0;
    constraint[0].y = 0;
    constraint[1].x = 0;
    constraint[1].y = 0;

    /* find the next k such that no straight line from i to k */
    for (k=mod(i+2,path_length); k!=i; k=mod(k+1,path_length)) {

      if (i<path_length-1 && cyclic(k,i,pivk[i+1])) {
	goto foundk;
      }

      dir = (3+3*(path[k].x-path[mod(k-1,path_length)].x)+(path[k].y-path[mod(k-1,path_length)].y))/2;
      dir_list[dir]++;

      /* if all four "directions" have occurred, cut this path */
      if (dir_list[0] && dir_list[1] && dir_list[2] && dir_list[3]) {
	goto foundk;
      }

      cur.x = path[k].x - path[i].x;
      cur.y = path[k].y - path[i].y;

      /* see if current constraint is violated */
      if (xprod(constraint[0], cur) < 0 || xprod(constraint[1], cur) > 0) {
	goto foundk;
      }

      /* else, update constraint */
      if (abs(cur.x) <= 1 && abs(cur.y) <= 1) {
	/* no constraint */
      } else {
	off.x = cur.x + ((cur.y>=0 && (cur.y>0 || cur.x<0)) ? 1 : -1);
	off.y = cur.y + ((cur.x<=0 && (cur.x<0 || cur.y<0)) ? 1 : -1);
	if (xprod(constraint[0], off) >= 0) {
	  constraint[0] = off;
	}
	off.x = cur.x + ((cur.y<=0 && (cur.y<0 || cur.x<0)) ? 1 : -1);
	off.y = cur.y + ((cur.x>=0 && (cur.x>0 || cur.y<0)) ? 1 : -1);
	if (xprod(constraint[1], off) <= 0) {
	  constraint[1] = off;
	}
      }	
    }
  foundk:
    pivk[i] = mod(k-1,path_length);

  } /* for i */

  /* clean up: for each i, let furthest_straight_vertex[i] be the largest k such that for
     all i' with i<=i'<k, i'<k<=pivk[i']. */

  j=pivk[path_length-1];
  p->furthest_straight_vertex[path_length-1]=j;
  for (i=path_length-2; i>=0; i--) {
    if (cyclic(i+1,pivk[i],j)) {
      j=pivk[i];
    }
    p->furthest_straight_vertex[i]=j;
  }

  for (i=path_length-1; cyclic(mod(i+1,path_length),j,p->furthest_straight_vertex[i]); i--) {
    p->furthest_straight_vertex[i] = j;
  }

  return 0;
}
