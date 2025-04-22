resource(R) :- node_attr(_,R,_).

% Deploy each service in exactly one node
{ deploy(S,X): node(X) } = 1 :- service(S).

% hreq: hard requirements (can't be relaxed)
% sreq: soft requirements (can be relaxed)
req(S,E) :- hreq(S,E).
{ req(S,E) } :- sreq(S,E).
violation_cost(S,E,(1,1)) :- sreq(S,E).
:~ violation_cost(S,E,(C,L)), lift(S,E). [C@L,S,E]
lift(S,E) :- sreq(S,E), not req(S,E).

shared_resource(R) :- req(_,reserve(R,_)).

% Sum of all quantities Q of resource R reserved by services deployed in X 
% must be below availability of R on Q
:- node_attr(X,R,T), shared_resource(R), #sum+{Q,S: deploy(S,X), req(S,reserve(R,Q))} > T.
:- req(S,reserve(R,Q)), deploy(S,X), node_attr(X,R,V), V < Q.

:- req(S,eq(R,V)),  deploy(S,X), not node_attr(X,R,V).
:- req(S,neq(R,V)), deploy(S,X), node_attr(X,R,V).
:- req(S,lt(R,T)),  deploy(S,X), node_attr(X,R,V), V >= T.
:- req(S,gt(R,T)),  deploy(S,X), node_attr(X,R,V), V <= T.
:- req(S,gte(R,T)), deploy(S,X), node_attr(X,R,V), V < T.
:- req(S,lte(R,T)), deploy(S,X), node_attr(X,R,V), V > T.

:- req((S1,S2),eq(R,V)),  deploy(S1,X), deploy(S2,Y),  not link_attr(X,Y,R,V).
:- req((S1,S2),neq(R,V)), deploy(S1,X), deploy(S2,Y),  link_attr(X,Y,R,V).
:- req((S1,S2),lt(R,T)),  deploy(S1,X), deploy(S2,Y),  link_attr(X,Y,R,V), V >= T.
:- req((S1,S2),gt(R,T)),  deploy(S1,X), deploy(S2,Y),  link_attr(X,Y,R,V), V <= T.
:- req((S1,S2),gte(R,T)), deploy(S1,X), deploy(S2,Y),  link_attr(X,Y,R,V), V < T.
:- req((S1,S2),lte(R,T)), deploy(S1,X), deploy(S2,Y),  link_attr(X,Y,R,V), V > T.
