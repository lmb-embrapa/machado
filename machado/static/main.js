/*
 Copyright 2018 by Embrapa.  All rights reserved.

 This code is part of the machado distribution and governed by its
 license. Please see the LICENSE.txt and README.md files that should
 have been included as part of this package for licensing information.
 */

function machadoToggleText(x) {
  ec = x.childNodes[0].classList;
  down = 'fa-caret-down';
  up = 'fa-caret-up';
  if (ec.contains(down)) {
  	ec.remove(down);
  	ec.add(up);
  } else {
  	ec.remove(up);
  	ec.add(down);
  }
}